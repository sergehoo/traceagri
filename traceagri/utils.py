from googletrans import Translator


def translate_text(text, dest_language='en'):
    """
    Traduit un texte donné dans une langue cible.
    :param text: Texte en français.
    :param dest_language: Code de langue cible (ex : 'en' pour anglais, 'es' pour espagnol).
    :return: Texte traduit.
    """
    translator = Translator()
    try:
        translation = translator.translate(text, src='fr', dest=dest_language)
        return translation.text
    except Exception as e:
        return text  # Retourne le texte original en cas d'erreur
