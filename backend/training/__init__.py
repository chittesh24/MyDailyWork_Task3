# Lazy imports only — training modules require heavy ML deps (torch, pandas)
# Import explicitly in training scripts, not at startup
__all__ = ['CaptionDataset', 'get_data_loaders', 'Vocabulary', 'get_transforms']
