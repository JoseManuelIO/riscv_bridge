.PHONY: help build-all clean-all hello mpc-simple

help:
	@echo "riscv_bridge - PULP/RISC-V"
	@echo ""
	@echo "make hello       - Compilar Hello"
	@echo "make mpc-simple  - Compilar MPC Simple"
	@echo "make build-all   - Compilar todo"
	@echo "make clean-all   - Limpiar"

hello:
	@cd tests/hello_minimal && make all

mpc-simple:
	@cd tests/mpc_simple && make all

build-all: hello mpc-simple
	@echo "✅ Todo compilado"

clean-all:
	@cd tests/hello_minimal && make clean || true
	@cd tests/mpc_simple && make clean || true
	@echo "✓ Limpieza completada"
