

import json

from groq import Groq


class MultiChoiceQuiz():
    """
    This class provides `generate_quiz()`, an interface to generate a multiple choice quiz
    with the specifed number of questions within the provided academic context.
    """
    def __init__(self):
        super().__init__()

        self.client = Groq(api_key=json.load(open(".venv/model_credentials.json", "r"))["GROQ_API_KEY"]) # TODO Fix file path by release
        self.MODEL = "llama-3.1-8b-instant"

        self.num_questions: int = 10 # Default is 10
    
    
    def generate_quiz(self, quiz_context: str, num_questions: int) -> str:
        """
        This function returns a JSON string representing the multiple choice quiz.
        The quiz is generated based on the quiz context, and the number of questions
        are specified by the function caller.
        
        Args:
            quiz_context: str --> The academic context the quiz will be based on
            num_questions: int --> The number of questions asked within the quiz
        
        Returns:
            A JSON in the following format:

            {
                "question1": {
                    "Question": "Text prompt for question 1",
                    "A": "Text is first option for question 1",
                    "B": "Text is first option for question 1",
                    "C": "Text is first option for question 1",
                    "D": "Text is first option for question 1",
                    "Answer": "Text is answer for question 1",
                    "Explanation": "Text is explanation for answer"
                },
                "question2": {
                    "Question": "Text prompt for question 2",
                    "A": "Text is first option for question 2",
                    "B": "Text is first option for question 2",
                    "C": "Text is first option for question 2",
                    "D": "Text is first option for question 2",
                    "Answer": "Text is answer for question 2",
                    "Explanation": "Text is explanation for answer"
                }
            }
        """

        self.set_num_questions(num_questions=num_questions)
        
        prompt = f"""
            BEGINNING OF COURSE CONTENT\n\n
            {quiz_context}
            \n\nEND OF COURSE CONTENT
            """
        
        prompt=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        
        prompt.insert(
                0,
                {
                    "role": "system",
                    "content": self.get_system_prompt()
                }
            )

        response = self.client.chat.completions.create(
            messages=prompt,
            model=self.MODEL,
            response_format={"type": "json_object"}
        )

        return response.choices[0].message.content
    

    def get_schema(self) -> str:
        """
        Getter function for the LLM JSON schema prompt

        Args:
            None
        
        Returns:
            The LLM JSON schema prompt
        """

        schema = json.load(open("models/mutli-choice-quiz-schema.json", "r")) # TODO Fix file path by release

        return schema


    def get_system_prompt(self) -> str:
        """
        Getter function for the LLM system prompt

        Args:
            None
        
        Returns:
            The system prompt for the LLM
        """

        example_output = """
            "question1": {
                "Question": "Where is the city of Calgary located?",
                "A": "Montana, USA",
                "B": "Saskatchewan, Canada",
                "C": "Alberta, Canada",
                "D": "Washington, USA",
                "Answer": "C",
                "Explanation": "Calgary is located within the Canadian province of Alberta."
            },
            "question2": {
                "Question": "Where is the city of Vancouver located?",
                "A": "Alberta, Canada",
                "B": "British Colombia, Canada",
                "C": "Texas, USA",
                "D": "California, USA",
                "Answer": "B",
                "Explanation": "Vancouver is located within the Canadian province of British Colombia."
            },
            """
        
        system_prompt = f"""
            You are an university professor who specializes in making challenging, yet fair and intellectually stimulating
            multiple choice quizzes.

            You must design your quiz around the following numbered principles:
            1. Instruct students to select the “best answer” rather than the “correct answer”. By doing this, you acknowledge the fact that the distractors may have an element of truth to them and discourage arguments from students who may argue that their answer is correct as well.
            2. Use familiar language. The question should use the same terminology that was used in the course. Avoid using unfamiliar expressions or foreign language terms, unless measuring knowledge of such language is one of the goals of the question. Students are likely to dismiss distractors with unfamiliar terms as incorrect.
            3. Avoid giving verbal association clues from the stem in the key. If the key uses words that are very similar to words found in the stem, students are more likely to pick it as the correct answer.
            4. Avoid trick questions. Questions should be designed so that students who know the material can find the correct answer. Questions designed to lead students to an incorrect answer, through misleading phrasing or by emphasizing an otherwise unimportant detail of the solution, violate this principle.
            5. Make sure there is only one best answer. Avoid having two or more options that are correct, but where one is “more” correct than the others. The distractors should be incorrect answers to the question posed in the prompt.
            6. Make the distractors appealing and plausible. If the distractors are farfetched, students will too easily locate the correct answer, even if they have little knowledge. When testing for recognition of key terms and ideas keep the distractors similar in length and type of language as the correct solution. When testing conceptual understanding, distractors should represent common mistakes made by students.
            7. Randomly distribute the correct response. The exam should have roughly the same number of correct answers that are a's, b's, c's, and d's.
            8. Avoid using “all of the above”. If “all of the above” is an option and students know two of the options are correct, the answer must be “all of the above”. If they know one is incorrect, the answer must not be “all of the above”. A student may also read the first option, determine that it is correct, and be misled into choosing it without reading all of the options.
            9. Avoid negative wording. Students often fail to observe negative wording and it can confuse them. As a result, students who are familiar with the material often make mistakes on negatively worded questions. In general, avoid having any negatives in the stem or the options.
            10. Make sure distractors match the correct answer in terms of length, complexity, phrasing, and style.
            11. Avoid language in the options and stems that clues the correct answer.
            12. Make options similar in grammar, length, complexity, and style.
            13. Ensure questions are equally distributed across the provided course context and don't solely focus on a single topic.
            
            You will recieve the course content from which you should strictly base the quiz on. You should not include
            content or concepts not mentioned in the provided content.

            Your job is to generate {str(self.get_num_questions())} multiple choice questions based on the provided JSON schema. The output should be
            formatted as a JSON instance that conforms to the JSON below.

            As an example, for the schema: {self.get_schema()}, the proper output would look like this in structure:

            ```
            {example_output}
            ```

            Do not return any preamble or explanations, return only a pure JSON string surrounded by triple backticks (```).
            """
        
        return system_prompt
    

    def set_num_questions(self, num_questions: int) -> None:
        """
        Setter function for the number of questions

        Args:
            num_questions: int --> The number of questions to be generated in the quiz
        
        Returns:
            None
        """
        self.num_questions = num_questions
    

    def get_num_questions(self) -> int:
        """
        Getter function for the number of questions

        Args:
            None
        
        Returns:
            The number of questions to be generated in the quiz
        """
        return self.num_questions


# Test
def main():

    quiz_generator_mc = MultiChoiceQuiz()

    # Random historical info on computers
    text = """
        The history of computers spans centuries and reflects humankind's evolving ability to process information and solve complex problems. Early computational devices, such as the abacus (used as early as 2400 BCE in Mesopotamia), helped people perform basic arithmetic. In the 17th century, inventors like Blaise Pascal and Gottfried Wilhelm Leibniz developed mechanical calculators capable of performing addition, subtraction, multiplication, and division. These innovations laid the foundation for future advancements in computing.

        A major conceptual leap occurred in the 19th century with Charles Babbage, who designed the Analytical Engine—an early mechanical general-purpose computer. Though never built in his lifetime, it introduced key ideas like a central processing unit and memory. Around the same time, Ada Lovelace, often regarded as the world’s first computer programmer, wrote algorithms for the machine, demonstrating its potential beyond simple calculation.

        The 20th century saw the development of the first true electronic computers. In the 1940s, machines like the ENIAC (Electronic Numerical Integrator and Computer) and the Colossus were created to perform calculations at unprecedented speeds, primarily for military applications during World War II. These machines used vacuum tubes and were enormous, power-hungry, and difficult to maintain.

        In the decades that followed, computing technology advanced rapidly. The invention of the transistor in 1947 revolutionized computer design by replacing bulky vacuum tubes, enabling smaller and more reliable machines. Integrated circuits in the 1960s and microprocessors in the 1970s further accelerated this trend. Personal computers emerged in the late 1970s and early 1980s, with companies like Apple, IBM, and Microsoft shaping the modern computing landscape. Today’s computers are millions of times more powerful than their early ancestors and have become essential tools in nearly every aspect of life, from communication and entertainment to science and industry.
        """

    # Multi-Choice
    print(f"Multiple choice quiz:\n{quiz_generator_mc.generate_quiz(quiz_context=text, num_questions=5)}\n\n")

    # True/False
    # TODO

    # Fill-in-the-Blank
    # TODO


if __name__== "__main__":
    main()
