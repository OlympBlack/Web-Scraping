from services.supabase_client import supabase
from typing import List, Optional, Dict

class QuoteRepository:
    TABLE_NAME = "quotes"

    @staticmethod
    def insert_quote(quote: Dict) -> Optional[Dict]:
        """
        Insère une citation dans la table quotes.
        Evite les doublons sur le champ 'text'.
        quote: {
            "text": str,
            "author": str,
            "link": str
        }
        """
        # Vérifier si la citation existe déjà
        existing = supabase.table(QuoteRepository.TABLE_NAME)\
            .select("id")\
            .eq("text", quote["text"])\
            .execute()

        if existing.data and len(existing.data) > 0:
            return None  
        
        # Insérer la citation
        result = supabase.table(QuoteRepository.TABLE_NAME)\
            .insert(quote)\
            .execute()

        return result.data[0] if result.data else None

    @staticmethod
    def get_all_quotes() -> List[Dict]:
        """Récupère toutes les citations"""
        result = supabase.table(QuoteRepository.TABLE_NAME)\
            .select("*")\
            .execute()
        return result.data or []

    @staticmethod
    def count_quotes() -> int:
        """Compte le nombre de citations"""
        result = supabase.table(QuoteRepository.TABLE_NAME)\
            .select("id", count="exact")\
            .execute()
        return result.count or 0
