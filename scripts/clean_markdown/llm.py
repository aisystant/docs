from openai import OpenAI
from langsmith.wrappers import wrap_openai
from langchain import hub

# Wrap the OpenAI client for use with langsmith
openai_client = wrap_openai(OpenAI())

def run(prompt_template_name: str, prompt_args: dict, model="gpt-4o-mini"):
    # Load the prompt template from LangChain Hub
    template = hub.pull(prompt_template_name)
    
    # Format the template with the provided arguments.
    # This assumes the template is a string with placeholders, e.g., {markdown}
    prompt = template.format(**prompt_args)
    
    # Call the LLM with the formatted prompt.
    response = openai_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model,
    )
    
    # Return the message part of the first choice.
    return response.choices[0].message.content

# Example usage with the 'markdown-cleaner' template:
if __name__ == "__main__":
    prompt_template_name = "markdown-cleaner"
    prompt_args = {
        "markdown": """
        # Sample Markdown
        This is **bold** text and this is *italic* text.
        """
    }
    result = run(prompt_template_name, prompt_args)
    print(result)
