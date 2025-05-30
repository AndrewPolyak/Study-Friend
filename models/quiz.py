

import json

from groq import Groq


class MultiChoiceQuiz():
    def __init__(self):
        super().__init__()

        self.client = Groq(api_key=json.load(open(".venv/model_credentials.json", "r"))["GROQ_API_KEY"]) # TODO Fix file path by release
        self.MODEL = "llama-3.1-8b-instant"

        self.num_questions: int = 10 # Default is 10
    
    
    def generate_quiz(self, quiz_context: str, num_questions: int) -> str:
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
        schema = json.load(open("models/mutli-choice-quiz-schema.json", "r")) # TODO Fix file path by release

        return schema


    def get_system_prompt(self) -> str:
        example_output = """
            "question1": {
                "Question": "Where is the city of Calgary located?",
                "A": "Montana, USA",
                "B": "Saskatchewan, Canada",
                "C": "Alberta, Canada",
                "D": "Washington, USA"
            },
            "question2": {
                "Question": "Where is the city of Vancouver located?",
                "A": "Alberta, Canada",
                "B": "British Colombia, Canada",
                "C": "Texas, USA",
                "D": "California, USA"
            },
            """
        
        system_prompt = f"""
            You are an university professor who specializes in making challenging, yet fair and intellectually stimulating
            multiple choice quizzes. Your questions should force the test-taker to think, and all answers should seem equally
            feasible, prompting the user to think deeply and weigh their options, not see an obvious choice immediately.

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
        self.num_questions = num_questions
    

    def get_num_questions(self) -> int:
        return self.num_questions


def main():
    quiz_generator = MultiChoiceQuiz()

    text = """
        The history of computers spans centuries and reflects humankind's evolving ability to process information and solve complex problems. Early computational devices, such as the abacus (used as early as 2400 BCE in Mesopotamia), helped people perform basic arithmetic. In the 17th century, inventors like Blaise Pascal and Gottfried Wilhelm Leibniz developed mechanical calculators capable of performing addition, subtraction, multiplication, and division. These innovations laid the foundation for future advancements in computing.

        A major conceptual leap occurred in the 19th century with Charles Babbage, who designed the Analytical Engine—an early mechanical general-purpose computer. Though never built in his lifetime, it introduced key ideas like a central processing unit and memory. Around the same time, Ada Lovelace, often regarded as the world’s first computer programmer, wrote algorithms for the machine, demonstrating its potential beyond simple calculation.

        The 20th century saw the development of the first true electronic computers. In the 1940s, machines like the ENIAC (Electronic Numerical Integrator and Computer) and the Colossus were created to perform calculations at unprecedented speeds, primarily for military applications during World War II. These machines used vacuum tubes and were enormous, power-hungry, and difficult to maintain.

        In the decades that followed, computing technology advanced rapidly. The invention of the transistor in 1947 revolutionized computer design by replacing bulky vacuum tubes, enabling smaller and more reliable machines. Integrated circuits in the 1960s and microprocessors in the 1970s further accelerated this trend. Personal computers emerged in the late 1970s and early 1980s, with companies like Apple, IBM, and Microsoft shaping the modern computing landscape. Today’s computers are millions of times more powerful than their early ancestors and have become essential tools in nearly every aspect of life, from communication and entertainment to science and industry.
        """

    print(quiz_generator.generate_quiz(quiz_context=text, num_questions=5))


if __name__== "__main__":
    main()
