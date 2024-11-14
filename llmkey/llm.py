

from __future__ import annotations

import abc
import time
from typing import Type


import ollama
import openai

from . import credentials, errors


class Backend(abc.ABC):
    Stream: Type[ResponseStream]
    name: str
    needs_credentials: bool

    @abc.abstractmethod
    def next_model(self, current):
        raise NotImplementedError()

    @property
    def default_model(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def query(self, model, message) -> ResponseStream:
        raise NotImplementedError()

class ResponseStream(abc.ABC):
    @abc.abstractmethod
    def __iter__(self) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def close():
        raise NotImplementedError()

model_cache = {}
def get(backend):
    if backend not in model_cache:
        model_cache[backend] = MODEL_CLASSES[backend]()

    return model_cache[backend]


class OllamaBackend(Backend):
    name = "ollama"
    needs_credentials = False
    class Stream(ResponseStream):
        def __init__(self, model, query):
            self.query = query
            self._stream = None
            self.model = model

        def __iter__(self):
            self._stream = ollama.chat(model=self.model, messages=[
            {
                'role': 'user',
                'content': self.query,
            },
            ], stream=True)


            for chunk in self._stream:
                yield chunk['message']['content']

        def close(self):
            if self._stream:
                self._stream.close()

    def next_model(self, current):
        return list_next(self.models, current)

    @property
    def models(self):
        return sorted([x["model"] for x in ollama.list()["models"]])

    @property
    def default_model(self):
        return self.models[0]

    def query(self, model, query):
        return LlmQuery(self.Stream(model, query))


class OpenaiBackend(Backend):
    name = "openai"
    needs_credentials = True
    base_url = None
    class Stream(ResponseStream):
        def __init__(self, model, query, connection):
            self.model = model
            self.query = query
            self.client = None
            self.connection = connection
            self.response = None

        def __iter__(self):
            self.response = self.connection.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'user', 'content': self.query}
                ],
                stream=True  # this time, we set stream=True
            )

            for chunk in self.response:
                content = chunk.choices[0].delta.content
                if content is None:
                    continue
                yield content

        def close(self):
            if self.response:
                self.response.close()


    def __init__(self, ):
        self._connection = None
        self._models = []

    @property
    def connection(self):
        if self._connection is not None:
            return self._connection

        key = credentials.get_key(self.name)
        if key is None:
            raise errors.NoKey()
        else:
             self._connection = openai.OpenAI(
                 api_key=key,
                 base_url=self.base_url)
             return self._connection

    def next_model(self, current):
        return list_next(self.models, current)

    @property
    def models(self):
        if not self._models:
            self._models = sorted([x.id for x in self.connection.models.list()])
        return self._models

    def query(self, model, query):
        return LlmQuery(self.Stream(model, query, self.connection))

    @property
    def default_model(self):
        return "gpt-3.5-turbo"


class XaiBackend(OpenaiBackend):
    name = "xai"
    needs_credentials = True
    base_url = "https://api.x.ai/v1"
    class Stream(OpenaiBackend.Stream):
        pass

    @property
    def default_model(self):
        return "grok-base"


class LlmQuery:
    "Tracks a query"
    def __init__(self, stream):
        self.stream = stream
        self.cancelled = False
        self.reply_buffer = []
        self.finished = False
        self.start = None
        self.finished_time = None

    @property
    def duration(self):
        if self.start is None:
            return 0
        else:
            return (self.finished_time or time.time()) - self.start

    @property
    def bytes(self):
        return sum(len(x) for x in self.reply_buffer)

    @property
    def reply(self):
        if not self.finished:
            raise Exception("Not Finished")

        return "".join(self.reply_buffer)


    @property
    def peek(self):
        return "".join(self.reply_buffer)

    def cancel(self):
        self.cancelled = True

    def run(self):
        self.start = time.time()

        for chunk in self.stream: #pylint: disable=not-an-iterable

            self.reply_buffer.append(chunk)
            if self.cancelled:
                self.stream.close()
                return None

        return "".join(self.reply_buffer)


class Backends:
    backends = ["ollama", "openai", "xai"]
    default = "ollama"

    @classmethod
    def next(cls, backend):
        return list_next(cls.backends, backend)

def list_next(members, x):
    if x is None:
        return members[0]
    else:
        return members[(members.index(x) + 1) % len(members)]


MODEL_CLASSES = {
  "ollama": OllamaBackend,
  "openai": OpenaiBackend,
  "xai": XaiBackend
}
