# Fase 3B-3 — código aprobado, publicación real bloqueada

QAHttpJournal limita cuatro POST al webhook propio, persiste intención/resultado,
bloquea incertidumbre y no sigue redirecciones ni proxies. Core exige el ID,
versión y hash revisados, checkpoint previo, presupuesto y STOP antes del Coder;
publica por MCP, verifica versión activa, correlaciona cuatro ejecuciones distintas
y vuelve a verificar publicación. Suite protegida y Reviewer siguen siendo
requisitos para el checkpoint final. Mocks mantienen su etiqueta explícita.

Tests RED antes de implementar; 6 específicos PASS y regresión 118/118 PASS.
Revisión independiente SDK, Sol High, PASS: evidence/phase3b/reviews/3B3/review.json.
No defectos bloqueantes identificados en ese alcance local. Metadata interna
resumeToken/autenticación se filtra antes de persistencia, incluso JSON duplicado.

Ensayo en el proyecto REAL: STOP impide nuevas operaciones; se retiró el marcador
del ensayo. La reanudación encuentra presupuesto agotado y bloquea ANTES del Coder.
Una segunda reanudación no repite nada. Contadores idénticos: 17 MCP, 6 turnos,
0 POST. Evidencia: 3b3-real-stop-budget-resume.json y snapshot live-blocked.

Resultado de integración publicada: **PENDING, NO PUBLICADA**. La reparación real
del borrador consumió 6/6 mutaciones; no se amplía ese límite. Es una limitación
local del presupuesto elegido por el agente, no un fallo demostrado de n8n.

Acción preparada: reports/PHASE3B-PUBLICATION-PLAN.md. Completar la fase necesita
autorización explícita para una mutación MCP adicional, cuatro POST y ventana
de 20 minutos sobre el mismo ID/versión. Ningún nuevo workflow ni cambio de OAuth.
