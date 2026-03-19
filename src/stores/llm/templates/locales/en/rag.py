from string import Template

system_prompt = Template("\n".join([
    "You are a knowledgeable assistant tasked with answering questions based on retrieved documents.",
    "",
]))

document_prompt = Template("\n".join([
    "Document Number: $doc_number",
    "Document Text: $doc_text"
]))

footer_prompt = Template("\n".join([
    "Question: $query",
    "Guidelines:",
    "- Use only the context above to answer.",
    "- Do not make up information.",
    "- If the answer is not in the context, say \"I don't know based on the provided information.\"",
    "- Be clear and concise.",
    "",
    "Answer: "
]))