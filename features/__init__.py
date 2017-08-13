from .comment_char_statistics import CommentCharStatistics
from .text_char_statistics import TextCharStatistics
from .historic_features import HistoricFeatures
from .last_rev_statistics import LastRevStatistics
from .pronoun_statistics import PronounStatistics
from .sandbox_features import SandboxFeatures
from .url_statistics import UrlStatisticsFeatures
from .similarity_statistics import SimilarityStatistics
from .morph_statistics import MorphStatistics
from .link_statistics import LinkStatistics


FEATURES_LIST = {
    'comment_char_stat': CommentCharStatistics,
    'text_char_stat': TextCharStatistics,
    'historic_stat': HistoricFeatures,
    'last_rev_stat': LastRevStatistics,
    'pronoun_stat': PronounStatistics,
    'sandbox_stat': SandboxFeatures,
    'morph_stat': MorphStatistics,
    'sim_stat': SimilarityStatistics,
    'url_stat': UrlStatisticsFeatures,
    'link_stat': LinkStatistics
}
