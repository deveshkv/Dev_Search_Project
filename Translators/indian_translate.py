from googletrans import Translator, LANGUAGES

def translate_to_english_googletrans(text):
    """
    Translate any Indian language text to English using googletrans.
    """
    translator = Translator()
    try:
        result = translator.translate(text, dest='en')
        return result.text
    except Exception as e:
        print(f"[❌] Translation failed: {e}")
        return text


def get_indian_language_codes():
    """
    Returns a dictionary of Indian language names and their googletrans codes.
    This list is curated based on common Indian languages supported by Google Translate.
    """
    indian_languages = {
        'hindi': 'hi',
        'bengali': 'bn',
        'marathi': 'mr',
        'telugu': 'te',
        'tamil': 'ta',
        'gujarati': 'gu',
        'kannada': 'kn',
        'malayalam': 'ml',
        'punjabi': 'pa',
        'urdu': 'ur',
        'odia': 'or', # Formerly 'oriya'
        'assamese': 'as',
        'sanskrit': 'sa',
        'konkani': 'gom',
        'maithili': 'mai',
        'manipuri': 'mni', # Often Meiteilon
        'sindhi': 'sd',
        'sinhala': 'si', # Although primarily spoken in Sri Lanka, it's relevant in the Indian subcontinent context
        'dogri': 'doi',
        'bhojpuri': 'bho',
        'mizo': 'lus',
        'awadhi': 'awa',
        'marwari': 'mwr',
        # Note: Some newer additions like Bodo, Khasi, Kokborok, Tulu might require direct testing
        # as their specific codes might not be consistently mapped in older googletrans versions
        # or might have regional variations not explicitly listed in the standard LANGUAGES dict.
    }
    
    # You can also dynamically check, but the LANGUAGES dict might not always be exhaustive
    # for all regional variations or very recent additions by Google.
    # For a more robust check, you might compare against a manually maintained list
    # or rely on Google's official Cloud Translation API for the most up-to-date support.
    
    # Filter and confirm presence in googletrans.LANGUAGES
    supported_indian_languages = {}
    for lang_name, lang_code in indian_languages.items():
        if lang_code in LANGUAGES.values():
            supported_indian_languages[lang_name.capitalize()] = lang_code
        # else:
            # print(f"Warning: {lang_name} ({lang_code}) might not be directly supported by this googletrans version.")
            
    return supported_indian_languages


def translate_text_to_indian_languages(text, src_language='auto'):
    """
    Translates text into multiple Indian languages.

    Args:
        text (str): The text to be translated.
        src_language (str): The source language code (e.g., 'en' for English, 'auto' for auto-detect).
                             Defaults to 'auto'.

    Returns:
        dict: A dictionary where keys are language names and values are translated texts.
    """
    translator = Translator()
    indian_lang_codes = get_indian_language_codes()
    translations = {}

    print(f"Original Text: '{text}' (Source: {src_language})")
    print("-" * 50)

    for lang_name, lang_code in indian_lang_codes.items():
        try:
            translation = translator.translate(text, dest=lang_code, src=src_language)
            translations[lang_name] = translation.text
            print(f"{lang_name} ({lang_code}): {translation.text}")
        except Exception as e:
            translations[lang_name] = f"Error: {e}"
            print(f"{lang_name} ({lang_code}): Error during translation - {e}")
    
    return translations

if __name__ == "__main__":
    # Example usage:
    text_to_translate = "Hello, this is a test sentence for translation into various Indian languages."
    
    # Translate from English (auto-detected) to all supported Indian languages
    all_translations = translate_text_to_indian_languages(text_to_translate)
    
    print("\n" + "="*50 + "\n")
    print("Summary of Translations:")
    for lang, translated_text in all_translations.items():
        print(f"{lang}: {translated_text}")

    print("\n" + "="*50 + "\n")
    text_to_translate_hindi = "भारत एक महान देश है।"
    print("Translating Hindi text to other Indian languages:")
    translate_text_to_indian_languages(text_to_translate_hindi, src_language='hi')
