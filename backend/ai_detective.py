import os
import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import httpx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("terradetective.ai_detective")

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
TARGET_OLLAMA_MODEL = "qwen3:8b"

class VerdictResult(str):
    """
    Subclasses str for 100% backward compatibility with all existing string assertions,
    while providing structured Story Mode attributes: headline, plain_summary, scientific_briefing.
    """
    def __new__(cls, scientific_briefing: str, headline: str = "", plain_summary: str = ""):
        instance = super().__new__(cls, scientific_briefing)
        instance.scientific_briefing = scientific_briefing
        instance.headline = headline
        instance.plain_summary = plain_summary
        return instance

    def to_dict(self) -> Dict[str, str]:
        return {
            "headline": self.headline,
            "plain_summary": self.plain_summary,
            "scientific_briefing": self.scientific_briefing
        }

class AIDetective:
    def __init__(self, catalog_variables: List[Dict[str, Any]]):
        import copy
        self.variables = copy.deepcopy(catalog_variables)
        self._enrich_variables_with_local_parameters()

        # 1. Initialize Dual Variable Matcher (Dense all-MiniLM-L6-v2 with TF-IDF fallback)
        self.dense_matcher_available = False
        self.embedding_model = None
        self.precomputed_embeddings = None
        self._init_dense_matcher_with_fallback()

        # 2. Probe Local Ollama REST API
        self.local_llm_info = self.probe_local_llm()

    def _enrich_variables_with_local_parameters(self):
        """Includes local verified satellite parameters in the recommendation corpus."""
        existing_ids = {v.get("identifier") for v in self.variables}
        local_additions = [
            {
                "identifier": "NDVI",
                "name": "MODIS Normalized Difference Vegetation Index",
                "simple_label": "Plant Canopy Greenness",
                "category_icon": "vegetation",
                "units": "index",
                "category": "Biosphere / Vegetation",
                "description": "Vegetation canopy density, leaf area index, crop health, forest cover, deforestation, greening trends.",
                "detective_hint": "Declines indicate forest clearance, drought stress, or logging; increases in drylands indicate irrigated agriculture.",
                "climatology_range": [-0.2, 1.0],
                "primary_sat_model": "Terra MODIS (MOD13A3.061)"
            },
            {
                "identifier": "LST_DAY",
                "name": "MODIS Daytime Land Surface Temperature",
                "simple_label": "Daytime Land Temperature",
                "category_icon": "heat",
                "units": "K",
                "category": "Thermal / Surface",
                "description": "Direct radiative surface skin temperature, urban heat island, deforestation warming, thermal shock.",
                "detective_hint": "Surface skin warming directly reflects loss of tree canopy evaporative cooling and higher Bowen ratios.",
                "climatology_range": [260.0, 335.0],
                "primary_sat_model": "Terra MODIS (MOD11A2.061)"
            },
            {
                "identifier": "GPM_PRECIP",
                "name": "GPM IMERG High-Resolution Precipitation",
                "simple_label": "Satellite Precipitation Rate",
                "category_icon": "rain",
                "units": "mm/hr",
                "category": "Hydrology / Precipitation",
                "description": "Satellite radar and microwave precipitation estimates, cloudbursts, monsoon divergence, meteorological drought.",
                "detective_hint": "Disentangles whether regional drying is driven by atmospheric rainfall deficits or soil moisture mismanagement.",
                "climatology_range": [0.0, 2.5],
                "primary_sat_model": "NASA / JAXA GPM IMERGM v07"
            },
            {
                "identifier": "GLDAS_ROOTMOIST",
                "name": "GLDAS Noah Root Zone Soil Moisture",
                "simple_label": "Subsurface Soil Moisture",
                "category_icon": "water",
                "units": "kg/m^2",
                "category": "Hydrology / Groundwater",
                "description": "Subsurface root zone water content (0-100cm), deep aquifer recharge, agricultural water depletion.",
                "detective_hint": "Directly reveals groundwater over-extraction hidden behind surface crop greening paradoxes.",
                "climatology_range": [50.0, 600.0],
                "primary_sat_model": "NASA GES DISC GLDAS Noah v2.1"
            }
        ]
        for item in local_additions:
            if item["identifier"] not in existing_ids:
                self.variables.append(item)

    def _init_dense_matcher_with_fallback(self):
        """
        Loads sentence-transformers/all-MiniLM-L6-v2 to pre-compute 384-dimensional embeddings.
        Automatically falls back to scikit-learn TF-IDF if model is offline or un-cached.
        """
        # Always build TF-IDF matrix as instant deterministic fallback
        self.corpus = []
        self.doc_ids = []
        for var in self.variables:
            text = (
                f"{var.get('identifier', '')} "
                f"{var.get('name', '')} "
                f"{var.get('category', '')} "
                f"{var.get('description', '')} "
                f"{var.get('detective_hint', '')}"
            )
            self.corpus.append(text)
            self.doc_ids.append(var.get("identifier"))

        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)

        # Attempt to load local SentenceTransformer all-MiniLM-L6-v2
        try:
            # Prevent remote network hangs in sandboxed or offline environments
            os.environ["HF_HUB_OFFLINE"] = "1"
            os.environ["TRANSFORMERS_OFFLINE"] = "1"
            from sentence_transformers import SentenceTransformer
            # Load local cached model on CPU
            logger.info("Initializing local SentenceTransformer ('all-MiniLM-L6-v2')...")
            try:
                self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
            except Exception:
                self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

            # Pre-encode all catalog variables into 384-dimensional normalized embeddings
            self.precomputed_embeddings = self.embedding_model.encode(
                self.corpus,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            self.dense_matcher_available = True
            logger.info("Successfully pre-encoded NASA variable catalog into 384-d dense embeddings.")
        except Exception as e:
            logger.warning(
                f"SentenceTransformer all-MiniLM-L6-v2 offline/failed ({e}). "
                "Engaging resilient Scikit-learn TF-IDF cosine matcher fallback."
            )
            self.dense_matcher_available = False
            self.embedding_model = None

    def probe_local_llm(self) -> Dict[str, Any]:
        """Probes for active Ollama runtime on localhost:11434 without cloud keys."""
        try:
            with httpx.Client(timeout=0.8) as client:
                res = client.get(OLLAMA_TAGS_URL)
                if res.status_code == 200:
                    models = [m.get("name") for m in res.json().get("models", [])]
                    has_target = any(TARGET_OLLAMA_MODEL in m for m in models)
                    active_model = TARGET_OLLAMA_MODEL if has_target else (models[0] if models else TARGET_OLLAMA_MODEL)
                    return {
                        "available": True,
                        "runtime": f"Ollama ({active_model})",
                        "models": models,
                        "active_model": active_model,
                        "target_model": TARGET_OLLAMA_MODEL
                    }
        except Exception:
            pass

        return {
            "available": False,
            "runtime": "Embedded Scientific Engine (Deterministic Local Physics)",
            "models": [],
            "active_model": "embedded-physics",
            "target_model": TARGET_OLLAMA_MODEL
        }

    def recommend_variables(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Maps a natural-language scientific query to top-k matching NASA variables
        using 384-d dense embeddings (with automatic TF-IDF fallback).
        Returns variables with relevance scores and concise 'why_selected' explanations.
        """
        if not query or len(query.strip()) < 2:
            return []

        clean_query = query.strip()
        similarities = None

        # 1. Try Dense MiniLM Embeddings
        if self.dense_matcher_available and self.embedding_model is not None:
            try:
                q_emb = self.embedding_model.encode([clean_query], normalize_embeddings=True)
                # Cosine similarity is dot product of normalized vectors
                similarities = np.dot(self.precomputed_embeddings, q_emb.T).flatten()
            except Exception as e:
                logger.warning(f"Dense encoding error ({e}), switching to TF-IDF.")
                similarities = None

        # 2. Resilient Fallback: TF-IDF Cosine Similarity
        if similarities is None:
            q_vec = self.vectorizer.transform([clean_query])
            similarities = cosine_similarity(q_vec, self.tfidf_matrix).flatten()

        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = []

        q_tokens = set(re.findall(r"\w+", clean_query.lower()))

        for idx in top_indices:
            score = float(similarities[idx])
            var = self.variables[idx]

            # Generate concise why_selected explanation
            doc_tokens = set(re.findall(r"\w+", self.corpus[idx].lower()))
            common = q_tokens.intersection(doc_tokens) - {"in", "the", "and", "why", "is", "of", "to", "how", "what", "are"}
            if common:
                why_selected = f"Matches inquiry keywords: {', '.join(sorted(list(common))[:3])} in {var.get('category', 'geophysical')} domain."
            else:
                why_selected = f"Matches {var.get('category', 'geophysical')} physical indicator characteristics."

            results.append({
                "identifier": var.get("identifier"),
                "name": var.get("name"),
                "simple_label": var.get("simple_label", var.get("name")),
                "category_icon": var.get("category_icon", "heat"),
                "units": var.get("units", ""),
                "category": var.get("category", ""),
                "description": var.get("description", ""),
                "detective_hint": var.get("detective_hint", ""),
                "climatology_range": var.get("climatology_range", [0.0, 100.0]),
                "primary_sat_model": var.get("primary_sat_model", "NASA Earth Observation Satellite System"),
                "relevance_score": round(max(float(score), 0.12), 3),
                "why_selected": why_selected,
                "match_rationale": why_selected # backward compatibility
            })

        return results

    def generate_detective_briefing(
        self,
        region_a_stats: Dict[str, Any],
        region_b_stats: Dict[str, Any],
        variable_meta: Dict[str, Any],
        label_a: str = "Region A",
        label_b: str = "Region B"
    ) -> VerdictResult:
        """
        Dual-Mode Local Scientific Verdict Generator using 'qwen3:8b' via Ollama REST API.
        Sends a structured prompt requesting a JSON object with:
          - headline: Plain-English human-impact takeaway (8th-grade level, zero jargon).
          - plain_summary: 2 short everyday sentences explaining what is happening and why it matters.
          - scientific_briefing: Exactly 3 crisp sentences with physical mechanism, decadal slopes, and p-values.
        Resilient Fallback: If Ollama times out or is offline, engages _synthesize_deterministic_verdict().
        """
        var_ident = variable_meta.get("identifier", "Variable")
        var_name = variable_meta.get("name", var_ident)
        units = variable_meta.get("units", "units")

        slope_a = region_a_stats.get("sens_slope_per_decade", 0.0)
        p_a = region_a_stats.get("p_value", 1.0)
        sig_a = region_a_stats.get("is_significant", False)

        slope_b = region_b_stats.get("sens_slope_per_decade", 0.0)
        p_b = region_b_stats.get("p_value", 1.0)
        sig_b = region_b_stats.get("is_significant", False)

        # 1. Attempt Local Ollama qwen3:8b Call for Structured JSON
        prompt = (
            f"You are a dual-mode NASA Earth System Detective. Analyze the regional divergence below and output a STRICT JSON OBJECT with three keys: 'headline', 'plain_summary', and 'scientific_briefing'.\n"
            f"- Parameter: {var_name} ({var_ident}, units: {units})\n"
            f"- {label_a}: Sen's Slope = {slope_a:+.3f} {units}/decade, Mann-Kendall p = {p_a:.4f} (Significant: {sig_a})\n"
            f"- {label_b}: Sen's Slope = {slope_b:+.3f} {units}/decade, Mann-Kendall p = {p_b:.4f} (Significant: {sig_b})\n\n"
            f"CRITICAL RULES:\n"
            f"1. 'headline': 10-12 words max, 8th-grade reading level, human-impact takeaway. Zero statistical jargon.\n"
            f"2. 'plain_summary': Exactly 2 short sentences explaining what is happening and why it matters in everyday language. Do NOT use technical words: Mann-Kendall, Sen's slope, p-value, Z-score, STL, NDVI, MODIS, GLDAS, MERRA-2.\n"
            f"3. 'scientific_briefing': Exactly 3 sentences. Sentence 1 explains the physical Earth system mechanism driving divergence. Sentence 2 states the exact decadal rates for {label_a} vs {label_b} ({slope_a:+.3f} vs {slope_b:+.3f} {units}/decade). Sentence 3 states whether shifts are statistically significant under Mann-Kendall (p < 0.05) vs seasonal noise.\n"
            f"Respond with ONLY valid JSON without markdown fences, explanation, or <think> tags."
        )

        try:
            with httpx.Client(timeout=4.0) as client:
                payload = {
                    "model": TARGET_OLLAMA_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a NASA scientific data analyst. Respond strictly in valid JSON matching the schema."},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 250
                    }
                }
                res = client.post(OLLAMA_CHAT_URL, json=payload)
                if res.status_code == 200:
                    raw_text = res.json().get("message", {}).get("content", "").strip()
                    # Strip any reasoning model <think> tags
                    clean_text = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()
                    clean_text = re.sub(r"^```(?:json)?\s*", "", clean_text, flags=re.IGNORECASE)
                    clean_text = re.sub(r"\s*```$", "", clean_text).strip()

                    try:
                        parsed = json.loads(clean_text)
                        if isinstance(parsed, dict) and "headline" in parsed and "plain_summary" in parsed and "scientific_briefing" in parsed:
                            briefing_str = parsed["scientific_briefing"].strip()
                            if len(briefing_str) > 30:
                                logger.info("Successfully generated dual-mode verdict JSON using local qwen3:8b via Ollama.")
                                return VerdictResult(
                                    scientific_briefing=briefing_str,
                                    headline=parsed["headline"].strip(),
                                    plain_summary=parsed["plain_summary"].strip()
                                )
                    except Exception as parse_err:
                        logger.debug(f"JSON parsing error from LLM output ({parse_err}). Falling back to text extractor.")

                    if len(clean_text) > 40:
                        fallback_head, fallback_plain = self._generate_plain_story(
                            var_ident, var_name, units, label_a, slope_a, label_b, slope_b
                        )
                        return VerdictResult(
                            scientific_briefing=clean_text,
                            headline=fallback_head,
                            plain_summary=fallback_plain
                        )
        except Exception as e:
            logger.info(f"Ollama qwen3:8b call offline or timed out ({e}). Engaging deterministic fallback synthesizer.")

        # 2. Resilient Deterministic Fallback Synthesis
        return self._synthesize_deterministic_verdict(
            var_ident=var_ident,
            var_name=var_name,
            units=units,
            label_a=label_a,
            slope_a=slope_a,
            p_a=p_a,
            sig_a=sig_a,
            label_b=label_b,
            slope_b=slope_b,
            p_b=p_b,
            sig_b=sig_b
        )

    def _generate_plain_story(
        self,
        var_ident: str,
        var_name: str,
        units: str,
        label_a: str,
        slope_a: float,
        label_b: str,
        slope_b: float
    ) -> Tuple[str, str]:
        """Generates plain-English headline and 2-sentence summary for Story Mode."""
        var_up = var_ident.upper()
        change_25_a = slope_a * 2.5
        change_25_b = slope_b * 2.5
        diff_25 = (slope_a - slope_b) * 2.5

        if "LST" in var_up or "TS" in var_up or "T2M" in var_up:
            if abs(diff_25) > 0.2:
                headline = f"{label_a} is warming significantly faster than {label_b} over the past 25 years."
            else:
                headline = f"Surface heat patterns are noticeably shifting across {label_a} and {label_b}."
            plain_summary = (
                f"Ground temperatures have shifted by {change_25_a:+.1f} {units} in {label_a} compared to {change_25_b:+.1f} {units} in {label_b} across 25 years. "
                f"Loss of tree cover reduces natural evaporative cooling, leaving land surfaces hotter and more vulnerable to heat stress."
            )
        elif "NDVI" in var_up:
            headline = "Farms look greener on the surface, but underground water is running dry."
            plain_summary = (
                f"Plant canopy density has shifted by {change_25_a:+.2f} in {label_a} compared to {change_25_b:+.2f} in {label_b} over the last 25 years. "
                f"While artificial irrigation makes crops appear vibrant from space, it often conceals severe water table depletion underneath."
            )
        elif "PRECIP" in var_up or "PRECTOT" in var_up:
            headline = f"Rainfall patterns are drifting apart between {label_a} and {label_b}."
            plain_summary = (
                f"Rainfall trends show an overall change of {change_25_a:+.2f} {units} in {label_a} versus {change_25_b:+.2f} {units} in {label_b} across 25 years. "
                f"Shifting seasonal storm tracks mean some farming basins face persistent drought while other areas see intensifying sudden downpours."
            )
        elif "MOIST" in var_up or "GWET" in var_up:
            headline = f"Deep underground water reserves in {label_a} are dropping over time."
            plain_summary = (
                f"Root-zone water storage has shifted by {change_25_a:+.1f} {units} across 25 years of observations. "
                f"Pumping groundwater faster than rainfall can replenish it creates a hidden, long-term water shortage for crops and communities."
            )
        else:
            headline = f"Long-term observations show diverging environmental paths for {label_a} and {label_b}."
            plain_summary = (
                f"Over 25 years of records, {label_a} shifted by {change_25_a:+.2f} {units} compared to {change_25_b:+.2f} {units} in {label_b}. "
                f"These contrasting trajectories show how local human activity and regional climate forces reshape the environment."
            )
        return headline, plain_summary

    def _synthesize_deterministic_verdict(
        self,
        var_ident: str,
        var_name: str,
        units: str,
        label_a: str,
        slope_a: float,
        p_a: float,
        sig_a: bool,
        label_b: str,
        slope_b: float,
        p_b: float,
        sig_b: bool
    ) -> VerdictResult:
        """
        Deterministic, mathematically grounded fallback synthesis.
        Populated with exact computed Sen's slopes, Mann-Kendall p-values,
        and plain-English Story Mode fields.
        """
        var_up = var_ident.upper()

        # Sentence 1: Physical Mechanism of Divergence
        if "LST" in var_up or "TS" in var_up or "T2M" in var_up:
            s1 = (
                f"{var_name} reveals pronounced thermodynamic divergence driven by surface energy repartitioning and the collapse of evaporative cooling across deforested regions."
            )
        elif "NDVI" in var_up:
            s1 = (
                f"{var_name} indicates biophysical canopy divergence driven by vegetative degradation in land-cleared zones contrasted with artificial irrigation intensification."
            )
        elif "PRECIP" in var_up or "PRECTOT" in var_up:
            s1 = (
                f"{var_name} displays spatial hydroclimatic divergence driven by convective monsoon steering and shifting moisture convergence zones."
            )
        elif "MOIST" in var_up or "GWET" in var_up:
            s1 = (
                f"{var_name} captures acute subsurface moisture divergence driven by anthropogenic groundwater over-extraction exceeding natural precipitation recharge."
            )
        else:
            s1 = (
                f"{var_name} illustrates distinct regional climate trajectories driven by localized boundary layer feedbacks and radiative equilibrium shifts."
            )

        # Sentence 2: Exact Decadal Rates
        s2 = (
            f"{label_a} is trending at {slope_a:+.3f} {units}/decade while {label_b} records a decadal trajectory of {slope_b:+.3f} {units}/decade (differential ΔS: {slope_a - slope_b:+.3f} {units}/decade)."
        )

        # Sentence 3: Statistical Significance vs Noise
        if sig_a and sig_b:
            s3 = (
                f"Both regional trajectories are statistically significant under the Mann-Kendall test (p={p_a:.4f} and p={p_b:.4f}, both p < 0.05), confirming genuine multi-decadal Earth system trends rather than seasonal noise."
            )
        elif sig_a:
            s3 = (
                f"The trend in {label_a} is statistically significant (Mann-Kendall p={p_a:.4f} < 0.05), whereas {label_b} (p={p_b:.4f}) reflects stationary seasonal noise."
            )
        elif sig_b:
            s3 = (
                f"The trend in {label_b} is statistically significant (Mann-Kendall p={p_b:.4f} < 0.05), while {label_a} (p={p_a:.4f}) remains within natural interannual variability thresholds."
            )
        else:
            s3 = (
                f"Neither region demonstrates statistical significance at the alpha=0.05 threshold (Mann-Kendall p={p_a:.4f} and p={p_b:.4f}), indicating that natural decadal oscillations dominate the record."
            )

        scientific_briefing = f"{s1} {s2} {s3}"
        headline, plain_summary = self._generate_plain_story(
            var_ident, var_name, units, label_a, slope_a, label_b, slope_b
        )

        return VerdictResult(
            scientific_briefing=scientific_briefing,
            headline=headline,
            plain_summary=plain_summary
        )

    def generate_verdict(
        self,
        var_ident: str,
        var_name: str,
        units: str,
        location_label: str,
        metrics: Dict[str, Any]
    ) -> VerdictResult:
        """Single-series verdict synthesis (for /api/analyze/live) with Story Mode support."""
        slope_decade = metrics.get("sens_slope_per_decade", 0.0)
        p_val = metrics.get("p_value", 1.0)
        is_sig = metrics.get("is_significant", False)
        direction = metrics.get("trend_direction", "no trend")
        pct_shift = metrics.get("percent_shift", 0.0)
        total_25 = slope_decade * 2.5

        if is_sig:
            s1 = (
                f"Across {location_label}, {var_name} demonstrates a statistically significant {direction} trend "
                f"at a Sen's slope rate of {slope_decade:+.3f} {units}/decade (Mann-Kendall p={p_val:.4f}, total shift {pct_shift:+.1f}%)."
            )
        else:
            s1 = (
                f"In {location_label}, {var_name} exhibits stationary fluctuations with a non-significant drift of "
                f"{slope_decade:+.3f} {units}/decade (Mann-Kendall p={p_val:.4f}), failing to exceed natural variability thresholds."
            )

        var_up = var_ident.upper()
        if "T2M" in var_up or "TS" in var_up or "LST" in var_up:
            if slope_decade > 0:
                s2 = "This thermal acceleration is driven by positive net surface radiation imbalances and diminished latent heat cooling as vegetative transpiration or surface moisture declines."
            else:
                s2 = "The moderated thermal trend reflects enhanced evaporative cooling buffering surface temperatures against regional macro-warming forcing."
        elif "PRECIP" in var_up or "PRECTOT" in var_up:
            if slope_decade > 0:
                s2 = "Enhanced moisture advection and intensifying convective uplift are concentrating precipitation into heavier, less frequent precipitation episodes."
            else:
                s2 = "Persistent atmospheric anticyclonic blocking and shifting monsoon circulation paths are suppressing regional moisture convergence."
        elif "NDVI" in var_up:
            if slope_decade < 0:
                s2 = "Canopy degradation reflects continuous deforestation, biomass fragmentation, and dry-season desiccation exceeding natural forest regenerative capacity."
            else:
                s2 = "Canopy greening reflects intensified double-cropping and irrigation subsidies rather than natural climatic equilibrium."
        elif "MOIST" in var_up or "GWET" in var_up:
            if slope_decade < 0:
                s2 = "Severe sub-surface water drawdowns indicate that evapotranspirative demand and mechanical extraction substantially outpace seasonal precipitation recharge."
            else:
                s2 = "Positive soil moisture retention confirms adequate groundwater recharge and favorable catchment retention capacity."
        else:
            s2 = f"This trajectory reflects fundamental reorganizations in regional boundary layer equilibrium and mass-energy balance."

        if is_sig:
            s3 = (
                f"Trend Detective Recommendation: Correlate this {direction} {var_ident} signal against coupled hydrological and "
                f"surface radiation pillars to diagnose whether the system is approaching a critical regional ecological tipping point."
            )
        else:
            s3 = (
                f"Trend Detective Recommendation: High inter-annual noise masks underlying shifts; cross-examine with high-resolution "
                f"extreme event frequency metrics to isolate sub-seasonal impacts."
            )

        scientific_briefing = f"{s1} {s2} {s3}"

        # Story Mode Translation for single region
        if is_sig:
            if "T2M" in var_up or "LST" in var_up or "TS" in var_up:
                headline = f"{location_label} is experiencing confirmed long-term warming."
                plain_summary = (
                    f"Temperatures have changed by {total_25:+.1f} {units} over the past 25 years. "
                    f"This sustained heating impacts local agriculture, human comfort, and seasonal water cycles."
                )
            elif "NDVI" in var_up:
                headline = f"Plant cover in {location_label} shows significant multi-decadal changes."
                plain_summary = (
                    f"Vegetation greenness has shifted by {total_25:+.2f} over the last 25 years. "
                    f"These landscape transformations show how local land use and climate forcing reshape the natural environment."
                )
            elif "PRECIP" in var_up or "PRECTOT" in var_up:
                headline = f"Rainfall patterns in {location_label} show a confirmed multi-decadal trend."
                plain_summary = (
                    f"Precipitation has changed by {total_25:+.2f} {units} across the 25-year record. "
                    f"These shifts affect local water security, seasonal crop planning, and flood risks."
                )
            elif "MOIST" in var_up or "GWET" in var_up:
                headline = f"Soil and underground water levels in {location_label} are persistently shifting."
                plain_summary = (
                    f"Water reserves have changed by {total_25:+.1f} {units} across the 25-year record. "
                    f"Deep water drawdowns directly threaten future farming resilience and local drinking wells."
                )
            else:
                headline = f"{location_label} exhibits a confirmed long-term Earth system trend."
                plain_summary = (
                    f"Values have shifted by {total_25:+.2f} {units} over the past 25 years. "
                    f"This steady change indicates ongoing reorganizations in the regional environment."
                )
        else:
            headline = f"{location_label} remains within normal year-to-year climate variation."
            plain_summary = (
                f"Observed changes over 25 years ({total_25:+.2f} {units}) remain inside typical natural swings. "
                f"Current year-to-year fluctuations do not show a statistically permanent climate departure."
            )

        return VerdictResult(
            scientific_briefing=scientific_briefing,
            headline=headline,
            plain_summary=plain_summary
        )

    def generate_detective_guidance(self, query: str, recommendations: List[Dict[str, Any]]) -> str:
        """Produces natural language guidance on how to investigate the query."""
        if not recommendations:
            return "No matching NASA variables found. Try querying for temperature, precipitation, soil moisture, or vegetation."

        top_names = [f"'{r['name']}' ({r['identifier']})" for r in recommendations[:2]]
        return (
            f"To investigate '{query}', compare {top_names[0]} with {top_names[1]} across the target region. "
            f"Look for decouple points where surface indicators diverge from deeper atmospheric or hydrological drivers."
        )
