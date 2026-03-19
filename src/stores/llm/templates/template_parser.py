import os

class TemplateParser:
    def __init__(self, language: str, default_language: str):
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_language = default_language

        self.language = None
        self.set_language(language=language)

    def set_language(self, language: str):
        if not language:
            self.language = self.default_language

        language_dir_path = os.path.join(
            self.current_path,
            "locales",
            language
        )

        if os.path.exists(language_dir_path):
            self.language = language
        else:
            self.language = self.default_language

    def get(self, group, key, vars= {}):
        """Group: locale group/template file (rag)
            key: prompt type (system, docs, footer,...)
            vars: optional variables to the templates"""
        if not group or not key:
            return None
        
        group_path = os.path.join(self.current_path, "locales", self.language, f"{group}.py" )
        used_language = self.language

        if not os.path.exists(group_path):
            group_path = os.path.join(self.current_path, "locales", self.default_language, f"{group}.py" )
            used_language = self.default_language

        if not os.path.exists(group_path):
            return None
        
        module = __import__(f"stores.llm.templates.locales.{used_language}.{group}", fromlist=[group])

        if not module:
            return None
        
        key_attribute = getattr(module, key)

        return key_attribute.substitute(vars)