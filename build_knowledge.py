from engine.knowledge_base import KnowledgeBase

kb = KnowledgeBase()

knowledge = kb.build_knowledge_base()

kb.save_knowledge(knowledge)