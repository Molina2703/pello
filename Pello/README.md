# ATHIS DEV AUTOPILOT V1 — Prototipo local

La orden `pello.cmd supervised` implementa el ciclo acotado de Fase 2.
Ver [uso y límites](PHASE2.md) y [resultado observado](reports/PHASE2.md).
El ciclo real completo sigue pendiente de validación tras el bloqueo inicial
documentado; no se afirma que Pello V1 esté terminado.

> **Instalación local actual:** ver [INSTALL.md](INSTALL.md) y
> [resultados verificados](reports/INSTALLATION.md). Usar `setup.ps1` y
> `pello.cmd` para trabajar dentro del entorno virtual. El texto de abajo es la
> documentación original del prototipo; las instrucciones actuales y las
> limitaciones de la validación están en esos dos documentos.

## Qué construimos

Un supervisor de trabajos que carga una ficha de producto, desarrolla por medio de **Codex Python SDK** (o un motor mock para probar la orquestación), ejecuta una **suite independiente** de pruebas, proporciona el diagnóstico de fallos al desarrollador, repite el ciclo con límite, registra estado en SQLite y genera evidencia verificable.

**Estado de validación:** el ciclo `mock` sí está probado. El adaptador **Codex real no se ha autenticado ni ejecutado** en la máquina donde se creó este paquete. La primera prueba real tiene que hacerse en el computador del fundador, con sesión de Codex disponible.

La primera demostración usa 8 pruebas sobre `ClinicBooking`: confirmación, doble reserva, idempotencia, cancelación, disponibilidad, validaciones y concurrencia. Es un **motor local con datos ficticios**, no una integración de clínica real ni de Google Calendar.

## Instalación inicial

Requisitos: Python 3.10 o más nuevo, Git instalado y acceso a terminal. En Windows usa PowerShell; en macOS/Linux, Terminal.

1. Descomprimir el ZIP y abrir terminal **dentro** de `athis-dev-autopilot-v1`.
2. Comprobar Python: `python --version` (en algunos Windows se usa `py -3`).
3. Ejecutar el piloto sin consumir Codex:

```bash
python -m unittest discover -s tests -v
python -m athis_autopilot doctor
python -m athis_autopilot demo
```

Resultado esperado del demo: `LISTO_PARA_REVISION`, 2 intentos, 1 ciclo de corrección, 8 pruebas exitosas. Las pruebas del intento inicial **deben fallar**: es la evidencia de que el verificador detecta problemas.

## Activar Codex de verdad

Instalar el SDK oficial (la instalación necesita internet):

```bash
python -m pip install -r requirements-codex.txt
python -m athis_autopilot doctor
python -m athis_autopilot login
```

Abrir la URL mostrada y autenticar con la misma cuenta de ChatGPT Plus que utiliza Codex. Si el navegador no funciona, probar `python -m athis_autopilot login --device`. También puede reutilizar una sesión previamente iniciada en Codex; el login explícito facilita depurar.

**Primera ejecución autónoma real (sin API de pago y sin integraciones externas):**

```bash
python -m athis_autopilot start --spec examples/clinica/spec.json --suite examples/clinica/acceptance --mode codex
```

Para ver el estado más tarde:

```bash
python -m athis_autopilot status ID_DEL_TRABAJO
python -m athis_autopilot resume ID_DEL_TRABAJO
```

Tras el comando `start`, el proceso corre hasta aprobar, bloquearse o agotar límites **mientras el ordenador está encendido y el proceso sigue abierto**. No es necesario mantener ChatGPT abierto; si apagas el proceso, para continuar se usa `resume`. Esta V1 no instala automáticamente un servicio de arranque del sistema.

## Archivos y evidencias

```
athis-dev-autopilot-v1/
├── athis_autopilot/
│   ├── cli.py                # Comandos
│   ├── supervisor.py         # Máquina de estados y SQLite
│   ├── engines.py            # Adaptadores mock y Codex
│   └── codex_worker.py       # Proceso aislado por turno de Codex
├── examples/clinica/
│   ├── spec.json             # Requisitos definidos por humano
│   └── acceptance/           # Pruebas independientes, NO editables por el agente
├── tests/                    # Pruebas del propio orquestador
└── runtime/                  # Aparece tras iniciar (ignorada en Git)
    ├── jobs.sqlite3
    └── jobs/<job_id>/
        ├── product_spec.json
        ├── workspace/        # Aquí escribe Codex; repo Git independiente
        ├── acceptance/       # Fuera del workspace, protegido por hash
        ├── evidence/         # Logs de cada ciclo y uso reportado por SDK
        ├── thread_id.txt     # ID reanudable de Codex cuando aplica
        ├── report.json
        └── report.md
```

### Máquina de estados

`CREADO` → `IMPLEMENTANDO` → `VERIFICANDO` → `LISTO_PARA_REVISION` si aprueba. Si falla: `CORRIGIENDO` → `VERIFICANDO` (máximo 5 correcciones). Codex puede terminar en `BLOQUEADO` por autorización o límites; incidentes no resueltos terminan `REQUIERE_REVISION_TECNICA`. La tabla SQLite permite reanudar trabajos no terminales. Se conserva evidencia de cada intento. No se alteran criterios para obtener un resultado favorable.

### Seguridad y limitaciones

- V1: **solo desarrollo local, una ejecución a la vez, sin despliegues ni contacto con clientes**.
- Codex se ejecuta con `Sandbox.workspace_write` y `ApprovalMode.deny_all`: nunca solicita una elevación manual y tampoco debería salir del área de trabajo. Una limitación de permisos puede impedirle completar tareas legítimas.
- **Advertencia clave:** el verificador ejecuta Python generado por IA en un proceso de tu sistema. Un `subprocess` con timeout **NO es un contenedor de seguridad**. Para proyectos ajenos o código no confiable, ejecutar bajo usuario del sistema con mínimos privilegios o en un contenedor/VM desechable antes de aumentar permisos o añadir MCP. Ninguna credencial de producción debe estar visible para el proceso.
- El hash SHA-256 detecta cambios a la suite de aceptación, pero **no demuestra aislamiento contra código malicioso**. Las pruebas se mantienen fuera del workspace y son externas al desarrollador.
- La autenticación Plus no garantiza ejecuciones ilimitadas. Si la cuenta alcanza su cuota, el trabajo se bloquea; nunca se presupone API de pago. El SDK puede reportar tokens por turno; no se calcula un costo USD ficticio.
- Las fichas no deben contener credenciales, contraseñas ni tokens. Autenticación se realiza por fuera del proyecto. Existe una validación básica de nombres de claves, no un detector exhaustivo de secretos pegados como texto.
- Actualmente no existe límite global diario de tokens ni presupuestos monetarios reales: se limita la cantidad de ciclos y el tiempo por turno. Antes de habilitar un modo API pago, implementar medición y corte sobre facturación real.
- Interrupciones bruscas durante una operación podrían dejar un turno del lado del servidor todavía activo; reanudación es **best effort**, no exactly-once. No exponer operaciones con efectos externos hasta incorporar idempotencia y recuperación robusta.
- No modifica GitHub remoto, Google Drive, n8n, WhatsApp ni Google Calendar. Son integraciones posteriores a validar el piloto Codex.

## Criterios de aceptación de la V1

1. `demo` muestra un fallo real en las pruebas del intento 1.
2. La orquestación detecta el fallo y ejecuta un segundo intento sin nuevos prompts humanos.
3. El segundo intento aprueba las 8 pruebas independientes.
4. Las evidencias contienen un log por intento, la huella SHA-256 de pruebas y el historial Git del workspace.
5. Si se edita la suite tras registrar el trabajo, el supervisor impide la aprobación.
6. Una ejecución `codex` autenticada demuestra el mismo ciclo no preprogramado. **Pendiente de validación.**

## Próximo escalón (no incluido)

Completar una ejecución real en tu máquina, luego añadir aislamiento del verificador, integración n8n DEV/MCP, pruebas con APIs y Playwright, control de costes, interruptor de emergencia y notificaciones. Después, persistencia frente a reinicios y concurrencia.
