ANNOTATION_MAPPING = {
    "type": {"type": "keyword"},
    "created_by": {"type": "keyword"},
    "created_at": {"type": "date"},
    "updated_at": {"type": "date"},
}


DOCUMENTS_MAPPING = {
    "settings": {
        "analysis": {"analyzer": {"default": {"type": "english"}}},
        "index": {
            "knn": True,
            "knn.algo_param.ef_search": 512,
            "mapping.total_fields.limit": 2000,
        },
    },
    "mappings": {
        "dynamic_templates": [
            {
                "strings": {
                    "path_match": "*",
                    "match_mapping_type": "string",
                    "mapping": {"type": "keyword"},
                }
            }
        ],
        "properties": {
            # Haystack
            "embedding": {
                "type": "knn_vector",
                "dimension": 384,
                "method": {
                    "name": "hnsw",
                    "space_type": "cosinesimil",
                    "engine": "nmslib",
                },
            },
            # Data
            "venture_id": {"type": "keyword"},
            "dataset": {"type": "keyword"},
            "metadata": {"type": "object", "enabled": False},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            "scraped_at": {"type": "date"},
            "referer": {"type": "keyword"},
            "text": {"type": "text"},
            "abstract": {"type": "text"},
            "summary": {"type": "text"},
            "date": {"type": "text"},
            "title": {"type": "text"},
            "name": {"type": "text"},
            "content_type": {"type": "keyword"},
            "url": {"type": "keyword"},
            "uri": {"type": "keyword"},
            "storage_url": {"type": "keyword"},
            "type": {"type": "keyword"},
            "scraper": {"type": "keyword"},
            "document_source": {"type": "keyword"},
            "annotations": {
                "type": "nested",
                "properties": {
                    **ANNOTATION_MAPPING,
                    "tasks": {
                        "properties": {
                            "document_class": {"type": "keyword"},
                            "content_control": {"type": "keyword"},
                            "document_source": {"type": "keyword"},
                        },
                    },
                },
            },
        },
    },
}


INSIGHTS_MAPPING = {
    "settings": {
        "analysis": {"analyzer": {"default": {"type": "english"}}},
        "index": {
            "knn": True,
            "knn.algo_param.ef_search": 512,
            "mapping.total_fields.limit": 2000,
        },
    },
    "mappings": {
        "dynamic_templates": [
            {
                "strings": {
                    "path_match": "*",
                    "match_mapping_type": "string",
                    "mapping": {"type": "keyword"},
                }
            }
        ],
        "properties": {
            "venture_id": {"type": "keyword"},
            "dataset": {"type": "keyword"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            "text": {"type": "text"},
            "par_index": {"type": "integer"},
            "date": {"type": "text"},
            "title": {"type": "text"},
            "name": {"type": "text"},
            "content_type": {"type": "keyword"},
            "url": {"type": "keyword"},
            "document_id": {"type": "keyword"},
            "type": {"type": "keyword"},
            "document_class": {"type": "keyword"},
            "document_source": {"type": "keyword"},
            "scraper": {"type": "keyword"},
            "sentences": {"type": "text"},
            "n_sentences": {"type": "short"},
            "n_sent_tokens": {"type": "short"},
            "n_tokens": {"type": "short"},
            "embedding": {
                "type": "knn_vector",
                "dimension": 384,
                "method": {
                    "name": "hnsw",
                    "space_type": "cosinesimil",
                    "engine": "nmslib",
                },
            },
            "annotations": {
                "type": "nested",
                "properties": {
                    **ANNOTATION_MAPPING,
                    "tasks": {
                        "properties": {
                            "relations": {
                                "type": "object",
                                "properties": {
                                    "company_concept": {
                                        "type": "object",
                                        "properties": {
                                            "label": {"type": "keyword"},
                                            "id": {"type": "keyword"},
                                        },
                                    },
                                    "impact_concept": {
                                        "type": "object",
                                        "properties": {
                                            "label": {"type": "keyword"},
                                            "id": {"type": "keyword"},
                                        },
                                    },
                                    "relation": {"type": "keyword"},
                                    "logit": {"type": "float"},
                                },
                            },
                            "concepts": {
                                "type": "object",
                                "properties": {
                                    "company_concepts": {
                                        "properties": {
                                            "label": {"type": "keyword"},
                                            "id": {"type": "keyword"},
                                            "logit": {"type": "float"},
                                        }
                                    },
                                    "impact_concepts": {
                                        "properties": {
                                            "label": {"type": "keyword"},
                                            "id": {"type": "keyword"},
                                            "logit": {"type": "float"},
                                        }
                                    },
                                },
                            },
                            "entities": {"type": "object", "enabled": False},
                            "document_source": {"type": "keyword"},
                            "content_control": {"type": "keyword"},
                            "insight_class": {"type": "keyword"},
                        },
                    },
                },
            },
        },
    },
}

CONCEPTS_MAPPING = {
    "settings": {
        "analysis": {"analyzer": {"default": {"type": "english"}}},
        "index": {
            "knn": True,
            "knn.algo_param.ef_search": 512,
            "mapping.total_fields.limit": 2000,
        },
    },
    "mappings": {
        "dynamic_templates": [
            {
                "strings": {
                    "path_match": "*",
                    "match_mapping_type": "string",
                    "mapping": {"type": "keyword"},
                }
            }
        ],
        "properties": {
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            "created_by": {"type": "keyword"},
            "dbpedia_ids": {"type": "keyword"},
            "type": {"type": "keyword"},
            "scheme": {"type": "keyword"},
            "insight_count": {"type": "integer"},
            "taxonomy": {
                "type": "nested",
                "properties": {
                    "label": {"type": "text"},
                    "short_label": {"type": "keyword"},
                },
            },
            "label": {"type": "text"},
            "description": {"type": "text"},
            "keywords": {"type": "text"},
            "embedding": {
                "type": "knn_vector",
                "dimension": 384,
                "method": {
                    "name": "hnsw",
                    "space_type": "cosinesimil",
                    "engine": "nmslib",
                },
            },
        },
    },
}
