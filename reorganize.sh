#!/bin/bash
################################################################################
# Script para reorganizar el repositorio riscv_bridge
# Mueve archivos a sus ubicaciones correspondientes según la nueva estructura
################################################################################

set -e

echo "════════════════════════════════════════════════════════════"
echo "  Reorganizando repositorio riscv_bridge"
echo "════════════════════════════════════════════════════════════"
echo ""

# Directorio base
BASE_DIR="$HOME/riscv_bridge"
cd "$BASE_DIR"

echo "📁 Creando estructura de directorios..."

# Crear directorios si no existen
mkdir -p applications/mpc_acc
mkdir -p tests/mpc_simple
mkdir -p scripts
mkdir -p docs

echo "✓ Directorios creados"
echo ""

# ============================================================================
# 1. MOVER APLICACIÓN PRINCIPAL (MPC ACC)
# ============================================================================
echo "📦 Moviendo aplicación MPC ACC..."

if [ -f "mpc_acc_controller.c" ]; then
    mv mpc_acc_controller.c applications/mpc_acc/
    echo "  ✓ mpc_acc_controller.c → applications/mpc_acc/"
fi

if [ -f "mpc_acc.elf" ]; then
    mv mpc_acc.elf applications/mpc_acc/
    echo "  ✓ mpc_acc.elf → applications/mpc_acc/"
fi

if [ -f "riscv.ld" ]; then
    cp riscv.ld applications/mpc_acc/
    echo "  ✓ riscv.ld → applications/mpc_acc/ (copiado)"
fi

if [ -f "start.S" ]; then
    cp start.S applications/mpc_acc/
    echo "  ✓ start.S → applications/mpc_acc/ (copiado)"
fi

echo ""

# ============================================================================
# 2. MOVER TEST MPC SIMPLE
# ============================================================================
echo "🧪 Moviendo test MPC simple..."

if [ -f "mpc_acc_simple.c" ]; then
    mv mpc_acc_simple.c tests/mpc_simple/
    echo "  ✓ mpc_acc_simple.c → tests/mpc_simple/"
fi

echo ""

# ============================================================================
# 3. MOVER SCRIPTS
# ============================================================================
echo "📜 Moviendo scripts..."

for script in compile.sh run_mpc_gvsoc.sh rebuild_and_test.sh test_simple.sh; do
    if [ -f "$script" ]; then
        mv "$script" scripts/
        echo "  ✓ $script → scripts/"
    fi
done

for pyscript in *.py; do
    if [ -f "$pyscript" ] && [ "$pyscript" != "__pycache__" ]; then
        mv "$pyscript" scripts/
        echo "  ✓ $pyscript → scripts/"
    fi
done

echo ""

# ============================================================================
# 4. LIMPIAR ARCHIVOS DE BUILD Y LOGS
# ============================================================================
echo "🧹 Limpiando archivos temporales..."

# Archivos de build antiguos
for file in *.elf *.bin debug_*.debugInfo; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo "  ✓ Eliminado: $file"
    fi
done

# Logs y outputs
for logfile in *.log *.txt *.csv; do
    if [ -f "$logfile" ]; then
        rm -f "$logfile"
        echo "  ✓ Eliminado: $logfile"
    fi
done

# Config de GVSOC en raíz (se regenera automáticamente)
if [ -f "gvsoc_config.json" ]; then
    rm -f gvsoc_config.json
    echo "  ✓ Eliminado: gvsoc_config.json (se regenera automáticamente)"
fi

echo ""

# ============================================================================
# 5. CREAR MAKEFILES EN NUEVAS UBICACIONES
# ============================================================================
echo "📝 Creando Makefiles..."

# Makefile para mpc_simple (si no existe)
if [ ! -f "tests/mpc_simple/Makefile" ]; then
    cat > tests/mpc_simple/Makefile << 'EOF'
APP = mpc_acc_simple
APP_SRCS = mpc_acc_simple.c
APP_CFLAGS += -Os -g
APP_LDFLAGS += -Os -g

PULP_SDK_HOME ?= $(HOME)/PULP/pulp-sdk
RULES_DIR ?= $(PULP_SDK_HOME)/tools/rules

include $(RULES_DIR)/pmsis_rules.mk
EOF
    echo "  ✓ Creado: tests/mpc_simple/Makefile"
fi

# Makefile para mpc_acc (si no existe)
if [ ! -f "applications/mpc_acc/Makefile" ]; then
    cat > applications/mpc_acc/Makefile << 'EOF'
APP = mpc_acc_controller
APP_SRCS = mpc_acc_controller.c
APP_CFLAGS += -Os -g -I$(CURDIR)
APP_LDFLAGS += -Os -g

PULP_SDK_HOME ?= $(HOME)/PULP/pulp-sdk
RULES_DIR ?= $(PULP_SDK_HOME)/tools/rules

include $(RULES_DIR)/pmsis_rules.mk
EOF
    echo "  ✓ Creado: applications/mpc_acc/Makefile"
fi

echo ""

# ============================================================================
# 6. RESUMEN
# ============================================================================
echo "════════════════════════════════════════════════════════════"
echo "  ✅ REORGANIZACIÓN COMPLETADA"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Estructura final:"
echo ""
echo "📦 applications/"
echo "   └── mpc_acc/          # Aplicación MPC principal"
echo ""
echo "🧪 tests/"
echo "   ├── hello_minimal/    # Test básico GVSOC"
echo "   └── mpc_simple/       # Test MPC simplificado"
echo ""
echo "📜 scripts/              # Scripts de utilidades"
echo ""
echo "📚 docs/"
echo "   └── INDEX.md          # Documentación completa"
echo ""
echo "Archivos eliminados:"
echo "  - Binarios antiguos (*.elf, *.bin)"
echo "  - Logs y traces (*.log, *.txt, *.csv)"
echo "  - Configuraciones temporales"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  PRÓXIMOS PASOS"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "1. Probar aplicación principal:"
echo "   cd applications/mpc_acc"
echo "   make clean all run"
echo ""
echo "2. Probar tests:"
echo "   cd tests/hello_minimal && make clean all run"
echo "   cd tests/mpc_simple && make clean all run"
echo ""
echo "3. Ver documentación:"
echo "   cat docs/INDEX.md"
echo ""
