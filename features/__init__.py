from .comment_char_statistics import CommentCharStatistics
from .text_char_statistics import TextCharStatistics
from .historic_features import HistoricFeatures
from .last_rev_statistics import LastRevStatistics
from .pronoun_statistics import PronounStatistics


FEATURES_LIST = {
    'comment_char_stat': CommentCharStatistics,
    'text_char_stat': TextCharStatistics,
    'historic_stat': HistoricFeatures,
    'last_rev_stat': LastRevStatistics,
    'pronoun_stat': PronounStatistics
}
