import os
import re
import json
import pandas as pd
from dotenv import load_dotenv

from langchain.chat_models import AzureChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain_openai import AzureOpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA

# Import config
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import Config

# ─── 1. Helper: Robust JSON Extraction ─────────────────────────────────────────────
def extract_json(text: str):
    """
    Finds the first balanced JSON object or array in `text` (by bracket matching),
    then returns the parsed Python object. Raises ValueError if none found.
    """
    for start_idx, ch in enumerate(text):
        if ch in ("{", "["):
            open_char = ch
            close_char = "}" if ch == "{" else "]"
            balance = 0
            for end_idx in range(start_idx, len(text)):
                if text[end_idx] == open_char:
                    balance += 1
                elif text[end_idx] == close_char:
                    balance -= 1
                    if balance == 0:
                        snippet = text[start_idx : end_idx + 1]
                        return json.loads(snippet)
            break
    raise ValueError(f"No complete JSON object/array found in LLM output:\n{text}")

class CandidateEvaluator:
    def __init__(self):
        """Initialize the candidate evaluator with all necessary components"""
        # Load environment variables
        load_dotenv()
        os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
        os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT")
        os.environ["OPENAI_API_TYPE"] = "Azure"
        
        # Initialize LLM
        self.llm = AzureChatOpenAI(
            openai_api_version="2023-12-01-preview",
            azure_deployment="GPT-4O-50-1",
        )
        
        # Load rubrics and old scores
        self._load_rubrics_and_scores()
        
        # Build FAISS indexes
        self._build_faiss_indexes()
        
        # Setup evaluation chains
        self._setup_evaluation_chains()
        
        # Define question type mapping
        self.QUESTION_TYPE_MAP = {
            Config.QUESTIONS[0]: "Technical",
            Config.QUESTIONS[1]: "Technical",
            Config.QUESTIONS[2]: "Technical", 
            Config.QUESTIONS[3]: "Technical",
            Config.QUESTIONS[4]: "HR",
            Config.QUESTIONS[5]: "HR",
            Config.QUESTIONS[6]: "HR",
            Config.QUESTIONS[7]: "HR"
        }
    
    def _load_rubrics_and_scores(self):
        """Load rubrics and old evaluation scores"""
        # Technical rubric & old results
        with open(Config.TECH_RUBRIC_PATH, "r", encoding="utf-8") as f:
            self.tech_rubric = json.load(f)
        
        with open(Config.TECH_OLD_RESULTS_PATH, "r", encoding="utf-8") as f:
            tech_old = json.load(f)
        
        self.tech_past_scores = {
            entry["question"]: entry["evaluation"].get("overall_score", 0.0)
            for entry in tech_old
        }
        
        # HR rubric & old results
        with open(Config.HR_RUBRIC_PATH, "r", encoding="utf-8") as f:
            self.hr_rubric = json.load(f)
        
        with open(Config.HR_OLD_RESULTS_PATH, "r", encoding="utf-8") as f:
            hr_old = json.load(f)
        
        self.hr_past_scores = {
            entry["question"]: entry["evaluation"].get("overall_score", 0.0)
            for entry in hr_old
        }
    
    def _build_faiss_indexes(self):
        """Build FAISS indexes for both Technical and HR datasets"""
        # Load datasets
        self.df_tech = pd.read_csv(Config.TECH_CSV_PATH).dropna(subset=["question", "answer"])
        self.df_hr = pd.read_csv(Config.HR_CSV_PATH).dropna(subset=["question", "answer"])
        
        # Extract questions
        tech_questions = self.df_tech["question"].astype(str).tolist()
        hr_questions = self.df_hr["question"].astype(str).tolist()
        
        # Initialize embeddings
        self.embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
        
        # Build FAISS indexes
        self.tech_vectorstore = FAISS.from_texts(tech_questions, self.embeddings)
        self.tech_retriever = self.tech_vectorstore.as_retriever(search_kwargs={"k": 3})
        
        self.hr_vectorstore = FAISS.from_texts(hr_questions, self.embeddings)
        self.hr_retriever = self.hr_vectorstore.as_retriever(search_kwargs={"k": 3})
    
    def _setup_evaluation_chains(self):
        """Setup LangChain evaluation chains"""
        # Technical exact-match chain
        tech_match_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are an assistant that decides if a new Technical question exactly matches one in the dataset.
From these retrieved questions:
{context}

New Question:
{question}

Respond with **exactly**:
- YES: "<matched question>"
- NO
"""
        )
        self.tech_match_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.tech_retriever,
            chain_type_kwargs={"prompt": tech_match_prompt}
        )
        
        # Technical relevance chain
        tech_relevance_prompt = PromptTemplate(
            input_variables=["new_question", "candidates"],
            template="""
New question:
{new_question}

Here are 3 candidate questions retrieved from the Technical dataset:
{candidates}

For each candidate, respond with YES or NO if it's truly relevant to the new question.
Return a JSON array with only those candidate strings that are relevant.
Example: ["Q1 text","Q3 text"]
"""
        )
        self.tech_relevance_chain = LLMChain(llm=self.llm, prompt=tech_relevance_prompt)
        
        # HR exact-match chain
        hr_match_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are an assistant that decides if a new HR question exactly matches one in the HR dataset.
From these retrieved questions:
{context}

New Question:
{question}

Respond with **exactly**:
- YES: "<matched question>"
- NO
"""
        )
        self.hr_match_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.hr_retriever,
            chain_type_kwargs={"prompt": hr_match_prompt}
        )
        
        # HR relevance chain
        hr_relevance_prompt = PromptTemplate(
            input_variables=["new_question", "candidates"],
            template="""
New question:
{new_question}

Here are 3 candidate questions retrieved from the HR dataset:
{candidates}

For each candidate, respond with YES or NO if it's truly relevant to the new question.
Return a JSON array with only those relevant candidate strings.
Example: ["Tell me about yourself.","What are your strengths?"]
"""
        )
        self.hr_relevance_chain = LLMChain(llm=self.llm, prompt=hr_relevance_prompt)
    
    def evaluate_with_rubric(self, question: str, answer: str, rubric: list) -> dict:
        """
        Given a single question & answer and a rubric (list of {"name","description"}),
        calls the LLM three times for independent evaluations, then:
          - Averages each criterion's numeric "score" (rounded to two decimals).
          - Summarizes the three one-sentence rationales into a single concise rationale.
          - Computes "overall_score" as the average of all averaged criterion scores.
        """
        rubric_str = json.dumps(rubric, indent=2)
        eval_prompt = PromptTemplate(
            input_variables=["rubric", "question", "answer"],
            template="""
You are an objective assessor. Here is a rubric (JSON array):
{rubric}

Now evaluate this response.

Question:
{question}

Answer:
{answer}

For each rubric item, produce an object with:
- "name"       (same as criterion)
- "score"      (integer 0–100)
- "explanation" (one-sentence rationale)

Then compute "overall_score" as the average of all scores.

Return **only** the final JSON object with keys "scores" and "overall_score".
"""
        )
        
        runs = []
        for _ in range(3):
            chain = LLMChain(llm=self.llm, prompt=eval_prompt)
            raw = chain.run(
                rubric=rubric_str,
                question=question,
                answer=answer
            )
            parsed = extract_json(raw)
            runs.append(parsed)
        
        first_scores = runs[0]["scores"]
        combined_scores = []
        
        for crit_obj in first_scores:
            crit_name = crit_obj["name"]
            
            # Collect the three scores and explanations for this criterion
            score_values = []
            explanations = []
            for run in runs:
                match = next(item for item in run["scores"] if item["name"] == crit_name)
                score_values.append(match["score"])
                explanations.append(match["explanation"])
            
            # Average numeric scores
            avg_score = round(sum(score_values) / len(score_values), 2)
            
            # Summarize the three one‐sentence rationales into one concise sentence
            summary_prompt = PromptTemplate(
                input_variables=["exp0", "exp1", "exp2"],
                template="""
You have three one‐sentence rationales for the same evaluation criterion:
1) {exp0}
2) {exp1}
3) {exp2}

Please write a single, concise one‐sentence explanation that captures the essence of all three rationales.
Return **only** that one‐sentence summary.
"""
            )
            summary_chain = LLMChain(llm=self.llm, prompt=summary_prompt)
            raw_summary = summary_chain.run(
                exp0=explanations[0],
                exp1=explanations[1],
                exp2=explanations[2]
            )
            summarized_explanation = raw_summary.strip()
            
            combined_scores.append({
                "name": crit_name,
                "score": avg_score,
                "explanation": summarized_explanation
            })
        
        # Compute overall_score
        if combined_scores:
            overall = round(sum(item["score"] for item in combined_scores) / len(combined_scores), 2)
        else:
            overall = 0.0
        
        return {
            "scores": combined_scores,
            "overall_score": overall
        }
    
    def is_instructional(self, text: str) -> bool:
        """
        Detects if a given HR answer is actually meta-instructions rather than a real answer.
        """
        patterns = [
            r"^\s*(Start with|Remember that|BEST ANSWERS?|Best strategy|Example:|Remember, you|To answer this question|If you want to|The only right answer|To cover both|Many executives)",
            r"\b(you should|you must|always|never|exercise)\b"
        ]
        for pat in patterns:
            if re.search(pat, text, flags=re.IGNORECASE):
                return True
        return False
    
    def convert_to_sample_answer(self, question: str, instructional_text: str) -> str:
        """
        If an HR answer stored is actually meta-instructions, this function prompts the LLM
        to generate a concrete 1–2 paragraph sample answer.
        """
        sample_prompt = PromptTemplate(
            input_variables=["question", "instructions"],
            template="""
The following text is a set of instructions (meta-guidance) on how to answer an HR question:
{instructions}

The HR question is:
"{question}"

Please produce a 1–2 paragraph sample answer to that question, following those instructions,
but expressed as if a candidate actually answered it in an interview.
Return **only** the answer text.
"""
        )
        chain = LLMChain(llm=self.llm, prompt=sample_prompt)
        output = chain.run(question=question, instructions=instructional_text)
        return output.strip()
    
    def evaluate_question_answer(self, question: str, answer: str) -> dict:
        """
        Takes a (question, answer) pair, detects its type (Technical or HR), then:
          1. If answer is "I don't know" or < 3 words → zero scores.
          2. Else:
             a) Exact match check via FAISS+RetrievalQA
             b) If exact and old_score>70 → combine 70% old + 30% fresh rubric; else 100% fresh rubric.
             c) If no exact match → relevance check (top-3 FAISS via LLMChain). If relevant old exist → average old scores → combine 30% avg_old + 70% fresh rubric. Else → 100% fresh rubric.
        """
        q_type = self.QUESTION_TYPE_MAP.get(question)
        if q_type not in ("Technical", "HR"):
            raise ValueError(f"Question not found in predefined questions: {question}")
        
        if q_type == "Technical":
            old_scores_map = self.tech_past_scores
            old_df = self.df_tech
            old_match_chain = self.tech_match_chain
            old_relev_chain = self.tech_relevance_chain
            retriever = self.tech_retriever
            rubric = self.tech_rubric
        else:
            old_scores_map = self.hr_past_scores
            old_df = self.df_hr
            old_match_chain = self.hr_match_chain
            old_relev_chain = self.hr_relevance_chain
            retriever = self.hr_retriever
            rubric = self.hr_rubric
        
        # Pre-check "I don't know" or very short answer
        normalized = answer.strip().lower()
        if normalized in ["i don't know", "i don't know", "idk", "no idea"] or len(normalized.split()) < 3:
            zero_breakdown = [
                {
                    "name": crit["name"],
                    "score": 0.0,
                    "explanation": "No substantive answer provided."
                }
                for crit in rubric
            ]
            return {
                "question": question,
                "type": q_type,
                "old_dataset_score": 0.0,
                "rubric_score": 0.0,
                "final_combined_score": 0.0,
                "rubric_breakdown": {
                    "scores": zero_breakdown,
                    "overall_score": 0.0
                }
            }
        
        result = {
            "question": question,
            "type": q_type,
            "old_dataset_score": 0.0,
            "rubric_score": 0.0,
            "final_combined_score": 0.0,
            "rubric_breakdown": None,
        }
        
        # Retrieve top-3 neighbors (for both exact & relevance)
        docs = retriever.get_relevant_documents(question)
        context = "\n".join(d.page_content for d in docs)
        
        # Exact-match check
        match_out = old_match_chain.run(question).strip()
        if match_out.upper().startswith("YES"):
            m = re.search(r'YES:\s*"(.*)"', match_out)
            exact_q = m.group(1) if m else None
            old_score = old_scores_map.get(exact_q, 0.0)
            result["old_dataset_score"] = old_score
            
            # Evaluate fresh rubric
            rub_report = self.evaluate_with_rubric(question, answer, rubric)
            rub_score = rub_report["overall_score"]
            result["rubric_score"] = rub_score
            
            if old_score > 70:
                # 70% old + 30% fresh rubric
                result["final_combined_score"] = round(0.7 * old_score + 0.3 * rub_score, 2)
            else:
                # old_score ≤ 70 → 100% fresh rubric
                result["final_combined_score"] = rub_score
            
            result["rubric_breakdown"] = rub_report
            return result
        
        # No exact match → Relevance check
        candidates_json = json.dumps([d.page_content for d in docs], indent=2)
        rel_raw = old_relev_chain.run(new_question=question, candidates=candidates_json)
        try:
            relevant_list = extract_json(rel_raw)
        except ValueError:
            relevant_list = []
        
        if not relevant_list:
            # No relevant → 100% fresh rubric
            rub_report = self.evaluate_with_rubric(question, answer, rubric)
            rub_score = rub_report["overall_score"]
            result["rubric_score"] = rub_score
            result["final_combined_score"] = rub_score
            result["rubric_breakdown"] = rub_report
            return result
        else:
            # Some relevant → compute average of their old overall_scores
            old_scores_accum = []
            for q_old in relevant_list:
                try:
                    a_old = old_df.loc[old_df.question == q_old, "answer"].iloc[0]
                except IndexError:
                    a_old = ""
                if q_type == "HR" and self.is_instructional(a_old):
                    # If the stored HR answer is instructional, convert to a sample answer
                    try:
                        a_old = self.convert_to_sample_answer(q_old, a_old)
                    except Exception:
                        pass
                old_rub_report = self.evaluate_with_rubric(q_old, a_old, rubric)
                old_scores_accum.append(old_rub_report["overall_score"])
            
            avg_old = sum(old_scores_accum) / len(old_scores_accum)
            result["old_dataset_score"] = avg_old
            
            new_rub_report = self.evaluate_with_rubric(question, answer, rubric)
            rub_score = new_rub_report["overall_score"]
            result["rubric_score"] = rub_score
            result["rubric_breakdown"] = new_rub_report
            
            combined = round(0.7 * rub_score + 0.3 * avg_old, 2)
            result["final_combined_score"] = combined
            return result
    
    def batch_evaluate(self, pairs: list) -> list:
        """
        Given a list of {"question": str, "answer": str}, returns a list of evaluation results.
        """
        results = []
        for entry in pairs:
            q = entry["question"]
            a = entry["answer"]
            try:
                res = self.evaluate_question_answer(q, a)
            except Exception as e:
                res = {
                    "question": q,
                    "type": self.QUESTION_TYPE_MAP.get(q, "Unknown"),
                    "error": str(e)
                }
            results.append(res)
        return results