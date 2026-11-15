"""Deterministic explanation provider without external model calls."""

from __future__ import annotations

from app.modules.ai.schemas import ExplainRequest, ExplainResponse


class TemplateProvider:
    """Build simple explanations from allow-listed metadata only."""

    def explain(self, request: ExplainRequest) -> ExplainResponse:
        context = request.context
        if request.language == "en":
            message = "Use these data as one signal, not as a guarantee of harvest."
            why = (
                f"The information is categorized as {context.category} "
                f"and comes from {context.source}."
            )
            audio = f"{message} {why}"
        else:
            message = "Usa estes dados como um sinal, não como garantia da colheita."
            why = f"A informação é da categoria {context.category} e vem de {context.source}."
            audio = f"{message} {why}"

        limitations = list(context.limitations)
        if context.resolution_warning:
            limitations.append(context.resolution_warning)
        limitations.append(
            "Os dados não garantem produtividade nem substituem a observação no campo."
        )
        return ExplainResponse(
            message_simple=message,
            audio_text=audio,
            why=why,
            limitations=limitations,
            technical_details={
                "category": context.category,
                "source": context.source,
                "dataset_version": context.dataset_version,
            },
        )

    def hint(self, request: ExplainRequest) -> ExplainResponse:
        response = self.explain(request)
        if request.context.category == "simulation":
            if request.language == "en":
                response.message_simple = "This is an educational example, not a field measurement."
                response.audio_text = response.message_simple
                response.why = "Use the challenge to explore an idea, then compare it with the real field."
            else:
                response.message_simple = "Este é um exemplo educativo, não uma medição no campo."
                response.audio_text = response.message_simple
                response.why = "Usa o desafio para explorar uma ideia e compara-a com a machamba real."
            response.limitations.append("Nenhum dado real de satélite foi usado nesta simulação.")
            return response

        if request.language == "en":
            response.message_simple = "Compare this signal with what you observe in the field."
            response.audio_text = response.message_simple
            response.why = "Satellite data describe a wider area; local observations add context."
        else:
            response.message_simple = "Compara este sinal com o que observas no campo."
            response.audio_text = response.message_simple
            response.why = (
                "Os dados de satélite descrevem uma área maior; "
                "a observação local acrescenta contexto."
            )
        return response
