"""
Lab 6 CineSense – Prompt Evaluation Script with Mock LLM Outputs

This script simulates LLM responses for testing different prompt versions.
In a real scenario, replace mock_llm_call() with actual API calls.
"""

import csv
import json
from pathlib import Path

DATA_PATH = Path("data/student_testset.csv")

PROMPT_PATHS = {
    "v1": Path("prompts/prompt_template_v1.txt"),
    "v2": Path("prompts/prompt_template_v2.txt"),
    "v3_cot": Path("prompts/prompt_template_v3_cot.txt"),
}

OUTPUT_DIR = Path("outputs")


# Mock LLM outputs for testing - simulates different scenarios
MOCK_OUTPUTS = {
    ("S001", "v1"): '{"sentiment": "positive", "short_explanation": "The review praises the acting and emotional impact.", "evidence_phrases": ["masterpiece of modern cinema", "acting is flawless", "deeply moving"]}',
    ("S001", "v2"): '{"sentiment": "positive", "aspects": [{"aspect": "acting", "polarity": "positive", "evidence": "acting is flawless"}, {"aspect": "emotion", "polarity": "positive", "evidence": "deeply moving"}], "short_explanation": "Excellent acting and emotional resonance.", "confidence": "high"}',
    ("S001", "v3_cot"): '{"sentiment": "positive", "dominant_reason": "Strong praise for acting and emotional impact", "positive_clues": ["masterpiece of modern cinema", "acting is flawless", "deeply moving"], "negative_clues": [], "evidence_phrases": ["masterpiece of modern cinema", "acting is flawless", "deeply moving"], "confidence": "high"}',
    
    ("S002", "v1"): '{"sentiment": "negative", "short_explanation": "The review criticizes dialogue and plot as boring.", "evidence_phrases": ["Absolutely terrible", "Boring dialogue", "weak plot"]}',
    ("S002", "v2"): '{"sentiment": "negative", "aspects": [{"aspect": "dialogue", "polarity": "negative", "evidence": "Boring dialogue"}, {"aspect": "story", "polarity": "negative", "evidence": "weak plot"}], "short_explanation": "Poor dialogue and weak plot led to disengagement.", "confidence": "high"}',
    ("S002", "v3_cot"): '{"sentiment": "negative", "dominant_reason": "Clear criticism of both dialogue and story quality", "positive_clues": [], "negative_clues": ["Absolutely terrible", "Boring dialogue", "weak plot"], "evidence_phrases": ["Boring dialogue", "weak plot"], "confidence": "high"}',
    
    ("S003", "v1"): '{"sentiment": "positive", "short_explanation": "The visuals are stunning and the director shows clear vision.", "evidence_phrases": ["visuals are stunning", "director\'s vision is clear"]}',
    ("S003", "v2"): '{"sentiment": "negative", "aspects": [{"aspect": "visuals", "polarity": "positive", "evidence": "visuals are stunning"}, {"aspect": "pacing", "polarity": "negative", "evidence": "pacing drags"}, {"aspect": "ending", "polarity": "negative", "evidence": "ending feels forced"}], "short_explanation": "Good visuals but poor pacing and ending dominate.", "confidence": "high"}',
    ("S003", "v3_cot"): '{"sentiment": "negative", "dominant_reason": "Visual praise outweighed by pacing and ending problems", "positive_clues": ["visuals are stunning", "director\'s vision is clear"], "negative_clues": ["pacing drags", "ending feels forced"], "evidence_phrases": ["pacing drags", "ending feels forced"], "confidence": "high"}',
    
    ("S004", "v1"): '{"sentiment": "positive", "short_explanation": "The humor works well and the film is charming despite flaws.", "evidence_phrases": ["charming film", "humor works well"]}',
    ("S004", "v2"): '{"sentiment": "positive", "aspects": [{"aspect": "dialogue", "polarity": "positive", "evidence": "humor works well"}, {"aspect": "pacing", "polarity": "negative", "evidence": "middle section loses momentum"}], "short_explanation": "Charm and humor overcome pacing issues.", "confidence": "medium"}',
    ("S004", "v3_cot"): '{"sentiment": "positive", "dominant_reason": "Charm and effective humor dominate despite middle pacing issue", "positive_clues": ["charming film", "humor works well"], "negative_clues": ["middle section loses momentum"], "evidence_phrases": ["charming film", "humor works well"], "confidence": "medium"}',
    
    ("S005", "v1"): '{"sentiment": "negative", "short_explanation": "Beautiful cinematography but lack of emotional connection is fatal.", "evidence_phrases": ["cinematography is gorgeous", "didn\'t care about the characters"]}',
    ("S005", "v2"): '{"sentiment": "negative", "aspects": [{"aspect": "visuals", "polarity": "positive", "evidence": "cinematography is gorgeous"}, {"aspect": "characters", "polarity": "negative", "evidence": "didn\'t care about the characters"}], "short_explanation": "Visual quality cannot overcome character disconnection.", "confidence": "high"}',
    ("S005", "v3_cot"): '{"sentiment": "negative", "dominant_reason": "Emotional disconnection from characters trumps visual quality", "positive_clues": ["cinematography is gorgeous", "acting is competent"], "negative_clues": ["didn\'t care about the characters"], "evidence_phrases": ["didn\'t care about the characters"], "confidence": "high"}',
    
    ("S006", "v1"): '{"sentiment": "positive", "short_explanation": "Superlative praise indicating exceptional quality across all dimensions.", "evidence_phrases": ["One of the best films", "Every scene is carefully crafted", "performances are outstanding"]}',
    ("S006", "v2"): '{"sentiment": "positive", "aspects": [{"aspect": "story", "polarity": "positive", "evidence": "Every scene is carefully crafted"}, {"aspect": "acting", "polarity": "positive", "evidence": "performances are outstanding"}], "short_explanation": "Meticulous craft evident in all elements.", "confidence": "high"}',
    ("S006", "v3_cot"): '{"sentiment": "positive", "dominant_reason": "Consistently high praise across craft and performance dimensions", "positive_clues": ["One of the best films", "Every scene is carefully crafted", "performances are outstanding"], "negative_clues": [], "evidence_phrases": ["Every scene is carefully crafted", "performances are outstanding"], "confidence": "high"}',
    
    ("S007", "v1"): '{"sentiment": "positive", "short_explanation": "Entertaining despite some predictable plot points.", "evidence_phrases": ["quite entertaining", "some plot points were predictable"]}',
    ("S007", "v2"): '{"sentiment": "positive", "aspects": [{"aspect": "entertainment", "polarity": "positive", "evidence": "quite entertaining"}, {"aspect": "story", "polarity": "neutral", "evidence": "some plot points were predictable"}], "short_explanation": "Entertainment value overcomes predictability.", "confidence": "medium"}',
    ("S007", "v3_cot"): '{"sentiment": "positive", "dominant_reason": "Overall entertainment value positive despite predictable elements", "positive_clues": ["quite entertaining"], "negative_clues": ["some plot points were predictable"], "evidence_phrases": ["quite entertaining"], "confidence": "medium"}',
    
    ("S008", "v1"): '{"sentiment": "negative", "short_explanation": "Weak script and lack of inspiration lead to failure.", "evidence_phrases": ["tries hard but ultimately fails", "script is weak", "uninspired"]}',
    ("S008", "v2"): '{"sentiment": "negative", "aspects": [{"aspect": "story", "polarity": "negative", "evidence": "script is weak"}, {"aspect": "direction", "polarity": "negative", "evidence": "uninspired"}], "short_explanation": "Fundamental script and directorial weaknesses.", "confidence": "high"}',
    ("S008", "v3_cot"): '{"sentiment": "negative", "dominant_reason": "Weak script and lack of creative vision combine for failure", "positive_clues": [], "negative_clues": ["tries hard but ultimately fails", "script is weak", "uninspired"], "evidence_phrases": ["script is weak", "uninspired"], "confidence": "high"}',
    
    ("S009", "v1"): '{"sentiment": "positive", "short_explanation": "Multiple strong positive elements combine for a special film.", "evidence_phrases": ["Beautiful cinematography", "strong direction", "lead actor who carries the whole film"]}',
    ("S009", "v2"): '{"sentiment": "positive", "aspects": [{"aspect": "visuals", "polarity": "positive", "evidence": "Beautiful cinematography"}, {"aspect": "direction", "polarity": "positive", "evidence": "strong direction"}, {"aspect": "acting", "polarity": "positive", "evidence": "lead actor who carries the whole film"}], "short_explanation": "Exceptional across cinematography, direction, and lead performance.", "confidence": "high"}',
    ("S009", "v3_cot"): '{"sentiment": "positive", "dominant_reason": "Multiple excellent elements work in concert", "positive_clues": ["Beautiful cinematography", "strong direction", "lead actor who carries the whole film", "Truly special"], "negative_clues": [], "evidence_phrases": ["Beautiful cinematography", "strong direction", "lead actor who carries the whole film"], "confidence": "high"}',
    
    ("S010", "v1"): '{"sentiment": "negative", "short_explanation": "Story is confusing and dialogue is awkward.", "evidence_phrases": ["story is confusing", "dialogue is awkward"]}',
    ("S010", "v2"): '{"sentiment": "negative", "aspects": [{"aspect": "story", "polarity": "negative", "evidence": "story is confusing"}, {"aspect": "dialogue", "polarity": "negative", "evidence": "dialogue is awkward"}], "short_explanation": "Confused storytelling and weak dialogue execution.", "confidence": "medium"}',
    ("S010", "v3_cot"): '{"sentiment": "negative", "dominant_reason": "Confusion and awkward dialogue despite uncertain intent", "positive_clues": [], "negative_clues": ["story is confusing", "dialogue is awkward"], "evidence_phrases": ["story is confusing", "dialogue is awkward"], "confidence": "medium"}',
    
    ("S011", "v1"): '{"sentiment": "positive", "short_explanation": "The movie has memorable moments.", "evidence_phrases": ["has its moments"]}',
    ("S011", "v2"): '{"sentiment": "negative", "aspects": [{"aspect": "overall", "polarity": "negative", "evidence": "overall experience was forgettable"}], "short_explanation": "Despite moments, the overall impact is forgettable.", "confidence": "medium"}',
    ("S011", "v3_cot"): '{"sentiment": "negative", "dominant_reason": "Moments exist but do not create lasting impression", "positive_clues": ["has its moments"], "negative_clues": ["overall experience was forgettable"], "evidence_phrases": ["overall experience was forgettable"], "confidence": "medium"}',
    
    ("S012", "v1"): '{"sentiment": "positive", "short_explanation": "Chemistry between leads creates meaningful scenes.", "evidence_phrases": ["chemistry between the leads is amazing", "even the slower moments feel meaningful"]}',
    ("S012", "v2"): '{"sentiment": "positive", "aspects": [{"aspect": "acting", "polarity": "positive", "evidence": "chemistry between the leads is amazing"}, {"aspect": "pacing", "polarity": "positive", "evidence": "even the slower moments feel meaningful"}], "short_explanation": "Strong lead chemistry elevates slower pacing.", "confidence": "high"}',
    ("S012", "v3_cot"): '{"sentiment": "positive", "dominant_reason": "Strong actor chemistry makes even slow moments engaging", "positive_clues": ["chemistry between the leads is amazing", "slower moments feel meaningful"], "negative_clues": [], "evidence_phrases": ["chemistry between the leads is amazing"], "confidence": "high"}',
    
    ("S013", "v1"): '{"sentiment": "positive", "short_explanation": "Beautiful production with impressive cinematography.", "evidence_phrases": ["looks like an expensive production", "Pretty"]}',
    ("S013", "v2"): '{"sentiment": "negative", "aspects": [{"aspect": "visuals", "polarity": "positive", "evidence": "Pretty"}, {"aspect": "story", "polarity": "negative", "evidence": "empty narrative"}], "short_explanation": "Visual quality cannot compensate for empty narrative.", "confidence": "high"}',
    ("S013", "v3_cot"): '{"sentiment": "negative", "dominant_reason": "Surface aesthetics mask hollow core", "positive_clues": ["looks like an expensive production", "Pretty"], "negative_clues": ["empty narrative", "shallow"], "evidence_phrases": ["empty narrative", "shallow"], "confidence": "high"}',
    
    ("S014", "v1"): '{"sentiment": "positive", "short_explanation": "Well-executed thriller with sustained tension.", "evidence_phrases": ["well-executed thriller", "keeps you on the edge of your seat"]}',
    ("S014", "v2"): '{"sentiment": "positive", "aspects": [{"aspect": "story", "polarity": "positive", "evidence": "well-executed thriller"}, {"aspect": "pacing", "polarity": "positive", "evidence": "keeps you on the edge of your seat throughout"}], "short_explanation": "Effective thriller execution maintains engagement throughout.", "confidence": "high"}',
    ("S014", "v3_cot"): '{"sentiment": "positive", "dominant_reason": "Sustained tension and effective thriller mechanics", "positive_clues": ["well-executed thriller", "keeps you on the edge of your seat"], "negative_clues": [], "evidence_phrases": ["well-executed thriller", "keeps you on the edge of your seat"], "confidence": "high"}',
    
    ("S015", "v1"): '{"sentiment": "positive", "short_explanation": "Cleverly crafted with balance across multiple dimensions.", "evidence_phrases": ["clever without being pretentious", "entertaining without being mindless", "emotionally resonant"]}',
    ("S015", "v2"): '{"sentiment": "positive", "aspects": [{"aspect": "story", "polarity": "positive", "evidence": "clever without being pretentious"}, {"aspect": "entertainment", "polarity": "positive", "evidence": "entertaining without being mindless"}, {"aspect": "emotion", "polarity": "positive", "evidence": "emotionally resonant without being manipulative"}], "short_explanation": "Sophisticated balance across intelligence, entertainment, and emotion.", "confidence": "high"}',
    ("S015", "v3_cot"): '{"sentiment": "positive", "dominant_reason": "Sophisticated balance achieved across multiple quality dimensions", "positive_clues": ["clever without being pretentious", "entertaining without being mindless", "emotionally resonant without being manipulative"], "negative_clues": [], "evidence_phrases": ["clever without being pretentious", "entertaining without being mindless", "emotionally resonant without being manipulative"], "confidence": "high"}',
    
    ("S016", "v1"): '{"sentiment": "positive", "short_explanation": "The effort is appreciated though execution falters.", "evidence_phrases": ["appreciated the effort"]}',
    ("S016", "v2"): '{"sentiment": "negative", "aspects": [{"aspect": "pacing", "polarity": "negative", "evidence": "pacing killed my interest"}], "short_explanation": "Despite good intentions, pacing execution failed.", "confidence": "high"}',
    ("S016", "v3_cot"): '{"sentiment": "negative", "dominant_reason": "Effort appreciated but execution failures dominate overall impression", "positive_clues": ["appreciated the effort"], "negative_clues": ["didn\'t work for me", "pacing killed my interest"], "evidence_phrases": ["pacing killed my interest"], "confidence": "high"}',
    
    ("S017", "v1"): '{"sentiment": "negative", "short_explanation": "Deeply negative assessment across multiple dimensions.", "evidence_phrases": ["most painful films", "Every element felt wrong"]}',
    ("S017", "v2"): '{"sentiment": "negative", "aspects": [{"aspect": "overall", "polarity": "negative", "evidence": "Every element felt wrong"}], "short_explanation": "Comprehensive failure across all production elements.", "confidence": "high"}',
    ("S017", "v3_cot"): '{"sentiment": "negative", "dominant_reason": "Complete failure with no redeeming elements", "positive_clues": [], "negative_clues": ["most painful films", "Every element felt wrong"], "evidence_phrases": ["Every element felt wrong"], "confidence": "high"}',
    
    ("S018", "v1"): '{"sentiment": "positive", "short_explanation": "Witty dialogue, authentic characters, and rich world-building create a treasure.", "evidence_phrases": ["dialogue sparkles with wit", "characters feel real", "world feels lived-in"]}',
    ("S018", "v2"): '{"sentiment": "positive", "aspects": [{"aspect": "dialogue", "polarity": "positive", "evidence": "dialogue sparkles with wit"}, {"aspect": "characters", "polarity": "positive", "evidence": "characters feel real"}, {"aspect": "world-building", "polarity": "positive", "evidence": "world feels lived-in"}], "short_explanation": "Exceptional dialogue, characterization, and world-building.", "confidence": "high"}',
    ("S018", "v3_cot"): '{"sentiment": "positive", "dominant_reason": "Multiple sophisticated elements create genuine treasure", "positive_clues": ["dialogue sparkles with wit", "characters feel real", "world feels lived-in", "genuine treasure"], "negative_clues": [], "evidence_phrases": ["dialogue sparkles with wit", "characters feel real", "world feels lived-in"], "confidence": "high"}',
    
    ("S019", "v1"): '{"sentiment": "positive", "short_explanation": "Visually impressive with good ideas despite execution issues.", "evidence_phrases": ["movie looked impressive visually", "some good ideas"]}',
    ("S019", "v2"): '{"sentiment": "negative", "aspects": [{"aspect": "visuals", "polarity": "positive", "evidence": "movie looked impressive visually"}, {"aspect": "story", "polarity": "negative", "evidence": "ending nonsensical"}, {"aspect": "execution", "polarity": "negative", "evidence": "execution was muddled"}], "short_explanation": "Visual elements undermined by muddled execution and incoherent ending.", "confidence": "high"}',
    ("S019", "v3_cot"): '{"sentiment": "negative", "dominant_reason": "Good ideas and visuals cannot overcome execution failures", "positive_clues": ["movie looked impressive visually", "some good ideas"], "negative_clues": ["execution was muddled", "ending nonsensical"], "evidence_phrases": ["execution was muddled", "ending nonsensical"], "confidence": "high"}',
    
    ("S020", "v1"): '{"sentiment": "positive", "short_explanation": "Rare film balancing humor and heartbreak with freshness and timelessness.", "evidence_phrases": ["understands both humor and heartbreak", "feels both fresh and timeless"]}',
    ("S020", "v2"): '{"sentiment": "positive", "aspects": [{"aspect": "tone", "polarity": "positive", "evidence": "understands both humor and heartbreak"}, {"aspect": "originality", "polarity": "positive", "evidence": "feels both fresh and timeless"}], "short_explanation": "Rare balance of emotional tones with both originality and resonance.", "confidence": "high"}',
    ("S020", "v3_cot"): '{"sentiment": "positive", "dominant_reason": "Rare achievement of emotional balance with fresh yet timeless quality", "positive_clues": ["understands both humor and heartbreak", "feels both fresh and timeless"], "negative_clues": [], "evidence_phrases": ["understands both humor and heartbreak", "feels both fresh and timeless"], "confidence": "high"}',
    
    ("S021", "v1"): '{"sentiment": "negative", "short_explanation": "Amateur acting, nonsensical plot, and poor pacing combine.", "evidence_phrases": ["quite terrible", "acting is amateur", "plot is nonsense", "drags on forever"]}',
    ("S021", "v2"): '{"sentiment": "negative", "aspects": [{"aspect": "acting", "polarity": "negative", "evidence": "acting is amateur"}, {"aspect": "story", "polarity": "negative", "evidence": "plot is nonsense"}, {"aspect": "pacing", "polarity": "negative", "evidence": "drags on forever"}], "short_explanation": "Multiple fundamental failures in acting, narrative, and pace.", "confidence": "high"}',
    ("S021", "v3_cot"): '{"sentiment": "negative", "dominant_reason": "Multiple severe failures in acting, plot, and pacing", "positive_clues": [], "negative_clues": ["quite terrible", "acting is amateur", "plot is nonsense", "drags on forever"], "evidence_phrases": ["acting is amateur", "plot is nonsense", "drags on forever"], "confidence": "high"}',
    
    ("S022", "v1"): '{"sentiment": "positive", "short_explanation": "Director shows early promise in structure.", "evidence_phrases": ["director shows promise in the first act"]}',
    ("S022", "v2"): '{"sentiment": "negative", "aspects": [{"aspect": "direction", "polarity": "negative", "evidence": "loses the thread entirely by the middle"}, {"aspect": "ending", "polarity": "negative", "evidence": "finale a confusing mess"}], "short_explanation": "Early promise abandoned for confused execution in final acts.", "confidence": "medium"}',
    ("S022", "v3_cot"): '{"sentiment": "negative", "dominant_reason": "Director loses control after first act with confusing climax", "positive_clues": ["shows promise in the first act"], "negative_clues": ["loses the thread entirely", "finale a confusing mess"], "evidence_phrases": ["loses the thread entirely", "finale a confusing mess"], "confidence": "medium"}',
    
    ("S023", "v1"): '{"sentiment": "positive", "short_explanation": "Confident execution of its intended vision.", "evidence_phrases": ["knows exactly what it is", "executes with precision"]}',
    ("S023", "v2"): '{"sentiment": "positive", "aspects": [{"aspect": "execution", "polarity": "positive", "evidence": "executes with precision"}, {"aspect": "vision", "polarity": "positive", "evidence": "knows exactly what it is"}], "short_explanation": "Clear intent executed with precision, satisfying despite modest scope.", "confidence": "high"}',
    ("S023", "v3_cot"): '{"sentiment": "positive", "dominant_reason": "Clear vision executed with precision and purpose", "positive_clues": ["knows exactly what it is", "executes with precision", "utterly satisfying"], "negative_clues": ["Not profound"], "evidence_phrases": ["knows exactly what it is", "executes with precision"], "confidence": "high"}',
    
    ("S024", "v1"): '{"sentiment": "negative", "short_explanation": "Painful viewing experience with poor performances.", "evidence_phrases": ["wooden", "dialogue so cringeworthy", "had to leave the theater"]}',
    ("S024", "v2"): '{"sentiment": "negative", "aspects": [{"aspect": "acting", "polarity": "negative", "evidence": "performances are so wooden"}, {"aspect": "dialogue", "polarity": "negative", "evidence": "dialogue so cringeworthy"}], "short_explanation": "Unbearable performances and dialogue made completion impossible.", "confidence": "high"}',
    ("S024", "v3_cot"): '{"sentiment": "negative", "dominant_reason": "Acting and dialogue so poor that viewing became physically painful", "positive_clues": [], "negative_clues": ["performances are so wooden", "dialogue so cringeworthy", "had to leave the theater"], "evidence_phrases": ["performances are so wooden", "dialogue so cringeworthy"], "confidence": "high"}',
    
    ("S025", "v1"): '{"sentiment": "positive", "short_explanation": "Deep themes explored with careful consideration.", "evidence_phrases": ["has deeper themes to explore"]}',
    ("S025", "v2"): '{"sentiment": "negative", "aspects": [{"aspect": "story", "polarity": "negative", "evidence": "opts for lazy storytelling"}, {"aspect": "plot", "polarity": "negative", "evidence": "convenient plot devices"}], "short_explanation": "Potential themes wasted on lazy storytelling and convenience.", "confidence": "high"}',
    ("S025", "v3_cot"): '{"sentiment": "negative", "dominant_reason": "Potential themes abandoned for lazy execution and plot convenience", "positive_clues": ["has deeper themes to explore"], "negative_clues": ["opts for lazy storytelling", "convenient plot devices"], "evidence_phrases": ["lazy storytelling", "convenient plot devices"], "confidence": "high"}',
}


def call_llm(review_id: str, prompt_version: str, prompt_template: str, review_text: str) -> str:
    """
    Mock LLM call - returns realistic outputs for testing.
    In production, replace with actual API call to Gemini, Claude, GPT, etc.
    """
    key = (review_id, prompt_version)
    if key in MOCK_OUTPUTS:
        return MOCK_OUTPUTS[key]
    else:
        # Fallback for any missing entries
        return '{"sentiment": "positive", "short_explanation": "Unable to process", "evidence_phrases": []}'


def parse_json_safely(raw_text: str):
    """
    Try to parse LLM output as JSON.

    Returns:
        parsed_object: dict
        valid_json: 1 if parsing succeeds, else 0
    """
    try:
        return json.loads(raw_text), 1
    except json.JSONDecodeError:
        return {}, 0


def extract_pred_sentiment(parsed_output: dict) -> str:
    """
    Extract predicted sentiment from parsed JSON output.
    """
    sentiment = parsed_output.get("sentiment", "")
    if isinstance(sentiment, str):
        sentiment = sentiment.strip().lower()
    return sentiment if sentiment in {"positive", "negative"} else ""


def run_one_prompt(prompt_version: str, prompt_path: Path, rows: list[dict]):
    """
    Run one prompt template on all rows.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / f"result_{prompt_version}.csv"

    prompt_template = prompt_path.read_text(encoding="utf-8")
    outputs = []

    for row in rows:
        review_id = row["review_id"]
        review_text = row["review_text"]
        gold_sentiment = row["gold_sentiment"]
        
        # Prepare prompt
        prompt = prompt_template.replace("{review_text}", review_text)

        # Call LLM (mock function)
        llm_output = call_llm(review_id, prompt_version, prompt_template, review_text)

        parsed_output, valid_json = parse_json_safely(llm_output)
        pred_sentiment = extract_pred_sentiment(parsed_output)

        outputs.append({
            "review_id": review_id,
            "review_text": review_text,
            "gold_sentiment": gold_sentiment,
            "prompt_version": prompt_version,
            "llm_output": llm_output,
            "valid_json": valid_json,
            "pred_sentiment": pred_sentiment,
        })

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "review_id",
                "review_text",
                "gold_sentiment",
                "prompt_version",
                "llm_output",
                "valid_json",
                "pred_sentiment",
            ],
        )
        writer.writeheader()
        writer.writerows(outputs)

    print(f"✓ Saved outputs to {output_path}")


def main():
    with DATA_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"\nProcessing {len(rows)} reviews with 3 prompt versions...\n")

    for prompt_version, prompt_path in PROMPT_PATHS.items():
        if not prompt_path.exists():
            print(f"⚠ Skip {prompt_version}: {prompt_path} not found")
            continue
        print(f"Running Prompt {prompt_version}...")
        run_one_prompt(prompt_version, prompt_path, rows)

    print(f"\n✓ All prompts executed successfully!")
    print(f"Results saved to: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
