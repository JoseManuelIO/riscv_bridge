# riscv_bridge - PULP/RISC-V Applications and Tests

Repositorio organizado de aplicaciones y tests para la plataforma PULP/RISC-V.

## 🗂️ Estructura del Repositorio

```
riscv_bridge/
├── applications/      # Aplicaciones principales
├── tests/            # Tests y ejemplos
├── scripts/          # Utilidades y scripts
└── docs/            # Documentación
```

## 🚀 Inicio Rápido

### Prerequisitos
```bash
export PULP_SDK_HOME=~/PULP/pulp-sdk
export PULP_RISCV_GCC_TOOLCHAIN=~/PULP/pulp-riscv-gnu-toolchain/install-32bit
source $PULP_SDK_HOME/configs/pulp-open.sh
```

### Compilar y Ejecutar
```bash
# Test básico
cd tests/hello_minimal
make clean all run

# Aplicación MPC
cd applications/mpc_acc
make clean all run
```

## 📚 Documentación Completa

Ver [docs/INDEX.md](docs/INDEX.md) para:
- Descripción detallada de cada componente
- Guías de uso
- Ejemplos
- Debugging
- Referencias

## 🎯 Componentes Principales

| Componente | Ubicación | Descripción |
|------------|-----------|-------------|
| MPC ACC Controller | `applications/mpc_acc/` | Controlador MPC completo con OSQP |
| Hello Minimal | `tests/hello_minimal/` | Test básico de GVSOC |
| MPC Simple | `tests/mpc_simple/` | Test MPC simplificado |
| Scripts | `scripts/` | Utilidades Python y Bash |

## 🔧 Comandos Útiles

```bash
# Limpiar todo
make clean-all

# Ejecutar todos los tests
make test-all

# Ver ayuda
make help
```

## 📝 Agregar Nuevos Componentes

Sigue la estructura existente y actualiza la documentación en `docs/INDEX.md`.

---

**Ver documentación completa en:** [docs/INDEX.md](docs/INDEX.md)
