from .comment_char_statistics import CommentCharStatistics
from .text_char_statistics import TextCharStatistics

FEATURES_LIST = {
    'comment_char_stat': CommentCharStatistics,
    'text_char_stat': TextCharStatistics
}