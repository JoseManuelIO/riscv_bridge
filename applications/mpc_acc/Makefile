################################################################################
# Makefile para mpc_acc_controller usando compilación manual RISC-V
################################################################################

APP = mpc_acc_controller
APP_SRCS = mpc_acc_controller.c

PULP_SDK_HOME ?= $(HOME)/PULP/pulp-sdk
TOOLCHAIN_DIR = $(HOME)/PULP/pulp-riscv-gnu-toolchain/install-32bit
BUILD_DIR = build

CC = $(TOOLCHAIN_DIR)/bin/riscv32-unknown-elf-gcc
AS = $(TOOLCHAIN_DIR)/bin/riscv32-unknown-elf-as
LD = $(TOOLCHAIN_DIR)/bin/riscv32-unknown-elf-gcc
OBJDUMP = $(TOOLCHAIN_DIR)/bin/riscv32-unknown-elf-objdump
SIZE = $(TOOLCHAIN_DIR)/bin/riscv32-unknown-elf-size

ARCH_FLAGS = -march=rv32imcxpulpv2 -mabi=ilp32
OPT_FLAGS = -Os -g
WARN_FLAGS = -Wall

DEFINES = \
	-DPULP_CHIP=PULP \
	-DPULP_CHIP_STR=pulp \
	-DCHIP_PULP=1 \
	-D__PULP__ \
	-D__RISCV__

INCLUDES = \
	-I$(PULP_SDK_HOME)/rtos/pulpos/common/include \
	-I$(PULP_SDK_HOME)/rtos/pmsis/pmsis_api/include \
	-I$(PULP_SDK_HOME)/rtos/pmsis/pmsis_bsp/include \
	-I$(PULP_SDK_HOME)/rtos/pulpos/pulp_hal/include \
	-I$(PULP_SDK_HOME)/rtos/pulpos/pulp_hal/include/hal/chips/pulp \
	-I$(PULP_SDK_HOME)/rtos/pulpos/pulp_archi/include \
	-I$(PULP_SDK_HOME)/rtos/pulpos/pulp_archi/include/archi/chips/pulp \
	-I$(CURDIR)/../../osqp/include

LINKER_SCRIPT = $(PULP_SDK_HOME)/rtos/pulpos/pulp/kernel/chips/pulp/link.ld

CFLAGS = $(ARCH_FLAGS) $(OPT_FLAGS) $(WARN_FLAGS) $(DEFINES) $(INCLUDES)
LDFLAGS = $(ARCH_FLAGS) -T$(LINKER_SCRIPT) -nostartfiles -lgcc

OBJS = $(BUILD_DIR)/$(APP).o

.PHONY: all clean run info disasm help

all: $(BUILD_DIR)/$(APP).elf
	@echo "✓ Compilación completa: $(BUILD_DIR)/$(APP).elf"

$(BUILD_DIR)/$(APP).o: $(APP_SRCS)
	@mkdir -p $(BUILD_DIR)
	@echo "CC $(APP_SRCS)"
	@$(CC) $(CFLAGS) -c $(APP_SRCS) -o $@

$(BUILD_DIR)/$(APP).elf: $(OBJS)
	@echo "LD $(APP).elf"
	@$(LD) $(LDFLAGS) $(OBJS) -o $@
	@$(SIZE) $@

info: $(BUILD_DIR)/$(APP).elf
	@echo ""
	@echo "═══════════════════════════════════════════════════════════"
	@echo "  INFORMACIÓN DEL EJECUTABLE"
	@echo "═══════════════════════════════════════════════════════════"
	@echo ""
	@echo "--- Tamaño ---"
	@$(SIZE) $(BUILD_DIR)/$(APP).elf
	@echo ""
	@echo "--- Secciones ---"
	@$(OBJDUMP) -h $(BUILD_DIR)/$(APP).elf | grep -E "\.text|\.data|\.bss|Idx"

disasm: $(BUILD_DIR)/$(APP).elf
	@$(OBJDUMP) -d $(BUILD_DIR)/$(APP).elf > $(BUILD_DIR)/$(APP)_disasm.txt
	@echo "✓ Desensamblado guardado en: $(BUILD_DIR)/$(APP)_disasm.txt"

clean:
	@rm -rf $(BUILD_DIR)
	@echo "✓ Limpieza completada"

run: all
	@echo ""
	@echo "═══════════════════════════════════════════════════════════"
	@echo "  ⚠️  Ejecución en GVSOC requiere PMSIS configurado"
	@echo "═══════════════════════════════════════════════════════════"
	@echo ""
	@echo "⚠️  Este programa requiere OSQP library (no incluida)"
	@echo "Para ejecutar, usar:"
	@echo "  1. source ~/PULP/pulp-sdk/configs/pulp-open.sh"
	@echo "  2. gapy --target=pulp --platform=gvsoc --program=$(BUILD_DIR)/$(APP).elf run"
	@echo ""

help:
	@echo ""
	@echo "═══════════════════════════════════════════════════════════"
	@echo "  Makefile para $(APP)"
	@echo "═══════════════════════════════════════════════════════════"
	@echo ""
	@echo "Targets:"
	@echo "  make all     - Compila $(APP_SRCS) → $(APP).elf"
	@echo "  make info    - Muestra información del ejecutable"
	@echo "  make disasm  - Genera desensamblado completo"
	@echo "  make clean   - Limpia archivos generados"
	@echo "  make help    - Muestra esta ayuda"
	@echo ""
	@echo "⚠️  NOTA: Requiere OSQP library compilada para RISC-V"
	@echo "El ELF se genera en: $(BUILD_DIR)/$(APP).elf"
	@echo ""
