# Estructura del Repositorio riscv_bridge

Este repositorio contiene implementaciones de controladores MPC (Model Predictive Control) para RISC-V/PULP, junto con tests y utilidades.

## 📁 Estructura de Directorios

```
riscv_bridge/
├── applications/          # Aplicaciones principales
│   └── mpc_acc/          # Controlador MPC para Adaptive Cruise Control
│       ├── mpc_acc_controller.c     # Implementación completa con OSQP
│       ├── Makefile                  # Build system
│       ├── riscv.ld                  # Linker script
│       ├── start.S                   # Assembly startup
│       └── README.md                 # Documentación específica
│
├── tests/                # Tests y ejemplos de prueba
│   ├── hello_minimal/    # Test básico de GVSOC
│   │   ├── hello_minimal.c
│   │   ├── Makefile
│   │   └── README.md
│   │
│   └── mpc_simple/       # Test simplificado de MPC
│       ├── mpc_acc_simple.c
│       ├── Makefile
│       └── README.md
│
├── docs/                 # Documentación
│   ├── INDEX.md          # Este archivo
│   ├── SETUP.md          # Guía de configuración
│   └── EXAMPLES.md       # Ejemplos de uso
│
└── scripts/              # Scripts de utilidades
    ├── compile.sh        # Script de compilación
    ├── run_mpc_gvsoc.sh  # Ejecutar MPC en GVSOC
    ├── rebuild_and_test.sh
    └── test_*.py         # Tests en Python
```

---

## 🎯 Clasificación de Componentes

### 1. **Aplicaciones Principales** (`applications/`)

#### **MPC ACC Controller** (`applications/mpc_acc/`)
- **Archivo principal:** `mpc_acc_controller.c`
- **Descripción:** Implementación completa de Model Predictive Control para Adaptive Cruise Control
- **Características:**
  - Usa OSQP solver
  - ~490 líneas de código
  - Optimización para RISC-V
  - Interface: stdin/stdout
- **Uso:**
  ```bash
  cd applications/mpc_acc
  make clean all run
  ```

---

### 2. **Tests** (`tests/`)

#### **Hello Minimal** (`tests/hello_minimal/`)
- **Archivo principal:** `hello_minimal.c`
- **Descripción:** Test básico para verificar GVSOC
- **Propósito:** Validar que el toolchain y GVSOC funcionan correctamente
- **Output esperado:**
  ```
  HELLO_START
  Testing GVSoC minimal execution
  HELLO_DONE
  ```
- **Uso:**
  ```bash
  cd tests/hello_minimal
  make clean all run
  make run-stats    # Con estadísticas
  ```

#### **MPC Simple** (`tests/mpc_simple/`)
- **Archivo principal:** `mpc_acc_simple.c`
- **Descripción:** Versión simplificada de MPC sin dependencias externas
- **Propósito:** Test rápido del algoritmo MPC básico (~105 líneas)
- **Características:**
  - Sin OSQP
  - Solo operaciones básicas
  - Ideal para debugging
- **Uso:**
  ```bash
  cd tests/mpc_simple
  make clean all run
  ```

---

### 3. **Scripts de Utilidades** (`scripts/`)

#### Scripts de Compilación:
- **`compile.sh`**: Compilación manual
- **`rebuild_and_test.sh`**: Recompila y ejecuta tests
- **`run_mpc_gvsoc.sh`**: Ejecuta MPC en GVSOC con configuración específica

#### Scripts de Testing (Python):
- **`test_hello.py`**: Test del hello_minimal
- **`test_mpc_controller.py`**: Test del controlador MPC
- **`quick_test.py`**: Test rápido de funcionalidades
- **`mpc_python_direct.py`**: Wrapper Python para MPC
- **`run_sharc_with_gvsoc.py`**: Integración con SHARC simulator

---

## 🚀 Guía de Uso Rápida

### Compilar y Ejecutar Aplicación Principal (MPC ACC):
```bash
cd applications/mpc_acc
make clean all run
```

### Ejecutar Tests:
```bash
# Test básico
cd tests/hello_minimal
make clean all run

# Test MPC simple
cd tests/mpc_simple
make clean all run
```

### Ver Estadísticas de Rendimiento:
```bash
cd tests/hello_minimal
make run-stats    # Genera VCD
make run-trace    # Trace de instrucciones
make run-profile  # Profiling completo
```

---

## 📊 Comparación de Implementaciones

| Característica | hello_minimal | mpc_simple | mpc_acc_controller |
|----------------|---------------|------------|-------------------|
| **Líneas de código** | ~20 | ~105 | ~490 |
| **Dependencias** | Ninguna | Ninguna | OSQP |
| **Propósito** | Test GVSOC | Test MPC básico | Aplicación real |
| **Complejidad** | Muy baja | Baja | Alta |
| **Tiempo de compilación** | <1s | <2s | ~5s |
| **Uso** | Validación | Testing | Producción |

---

## 🔧 Requisitos del Sistema

### Herramientas Necesarias:
- **PULP SDK**: Instalado en `~/PULP/pulp-sdk`
- **Toolchain RISC-V**: `~/PULP/pulp-riscv-gnu-toolchain/install-32bit`
- **GVSOC**: Simulador (incluido en PULP SDK)
- **Python 3.x**: Para scripts de testing

### Configuración:
```bash
# Configurar variables de entorno
export PULP_SDK_HOME=~/PULP/pulp-sdk
export PULP_RISCV_GCC_TOOLCHAIN=~/PULP/pulp-riscv-gnu-toolchain/install-32bit
export PATH=$PULP_RISCV_GCC_TOOLCHAIN/bin:$PATH

# Source PULP SDK
source $PULP_SDK_HOME/configs/pulp-open.sh
```

---

## 📝 Archivos Generados

Durante la compilación y ejecución se generan:

### Build artifacts:
- `BUILD/PULP/GCC_RISCV/`: Directorio de compilación
  - `*.o`: Archivos objeto
  - `*.elf`: Ejecutable RISC-V
  - `*.map`: Mapa de memoria

### Archivos de ejecución:
- `view.vcd`: Waveform para GTKWave (con `make run-stats`)
- `gvsoc_config.json`: Configuración de GVSOC
- `trace_file.txt`: Traces de ejecución
- `power_report.csv`: Reporte de consumo de energía
- `events.log`: Log de eventos del simulador

---

## 🎓 Flujo de Desarrollo

### Para agregar un nuevo test:
1. Crear directorio en `tests/nombre_test/`
2. Agregar archivo `.c` principal
3. Copiar y adaptar `Makefile` de `hello_minimal`
4. Crear `README.md` específico
5. Ejecutar: `make clean all run`

### Para agregar una nueva aplicación:
1. Crear directorio en `applications/nombre_app/`
2. Agregar archivos fuente
3. Configurar `Makefile` con dependencias
4. Documentar en `README.md`
5. Actualizar este `INDEX.md`

---

## 🐛 Debugging

### Ver código Assembly generado:
```bash
make disasm
# Genera archivo *_disasm.txt con todo el código desensamblado
```

### Ver información del ejecutable:
```bash
make info
# Muestra tamaño, secciones, símbolos, código main, etc.
```

### Ejecutar con traces detallados:
```bash
make run-trace
# Muestra cada instrucción ejecutada
```

---

## 📚 Referencias

- **PULP Platform**: https://pulp-platform.org/
- **RISC-V ISA**: https://riscv.org/
- **GVSOC Documentation**: En `$PULP_SDK_HOME/docs/`
- **OSQP Solver**: https://osqp.org/

---

## 🤝 Contribuciones

Para agregar nuevos ejemplos o mejoras:
1. Seguir la estructura de directorios establecida
2. Incluir `README.md` en cada directorio nuevo
3. Asegurar que `make clean all run` funcione
4. Actualizar esta documentación

---

## 📧 Contacto

Para preguntas o issues, revisar la documentación en `docs/` o consultar el README principal del repositorio.

---

**Última actualización:** Febrero 2026
**Versión del documento:** 1.0
