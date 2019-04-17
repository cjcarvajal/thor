import faust


class EmptyEvent(faust.Record, serializer='json'):
    code: int
