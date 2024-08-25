import os


TRACING_EXPORTER_ENDPOINT: str = os.environ.get("TRACING_EXPORTER_ENDPOINT", "")


def init_jaeger() -> bool:
    try:
        from opentelemetry.instrumentation.django import DjangoInstrumentor
        from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor
        from opentelemetry.instrumentation.logging import LoggingInstrumentor
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        from opentelemetry.instrumentation.celery import CeleryInstrumentor

        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk import resources
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider(
            resource=resources.Resource.create({resources.SERVICE_NAME: "djangoapp"})
        )
        trace.set_tracer_provider(provider)
        jaeger_exporter = OTLPSpanExporter(
            endpoint=TRACING_EXPORTER_ENDPOINT,
            insecure=True,
        )
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )

        DjangoInstrumentor().instrument(tracer_provider=trace.get_tracer_provider())
        PsycopgInstrumentor().instrument(tracer_provider=trace.get_tracer_provider())
        LoggingInstrumentor().instrument(tracer_provider=trace.get_tracer_provider())
        RequestsInstrumentor().instrument(trace_provider=trace.get_tracer_provider())
        CeleryInstrumentor().instrument(trace_provider=trace.get_tracer_provider())
    except Exception as e:
        print(f"TRACING NOT STARTED - {e}")
        return False
    else:
        return True
