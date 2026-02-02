# RISC-V MPC Controller con GVSoC

Sistema de control MPC (Model Predictive Control) ejecutando en simulador RISC-V GVSoC integrado con SHARC para Adaptive Cruise Control (ACC).

---

## 📋 Descripción General

Este proyecto implementa un controlador MPC para vehículos ACC que ejecuta en un procesador RISC-V simulado (PULP-open) usando GVSoC. El controlador recibe el estado del vehículo, calcula las fuerzas de control óptimas (aceleración/frenado), y devuelve los resultados para aplicar a la dinámica del vehículo.

### Características

- ✅ **Controlador MPC en C** optimizado para RISC-V bare-metal
- ✅ **Simulación en GVSoC** con PULP-open virtual platform
- ✅ **Integración con SHARC** para closed-loop simulation
- ✅ **Modelo ACC completo** con física vehicular realista
- ✅ **Optimización híbrida** grid search + gradient descent
- ✅ **Comunicación STDOUT** sin dependencias de librerías

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                  SHARC (Python Host)                    │
│  ┌──────────────┐         ┌──────────────┐            │
│  │   Dynamics   │◄────────┤   Simulator  │            │
│  │  (Vehicle)   │         │    Loop      │            │
│  └──────┬───────┘         └───────┬──────┘            │
│         │                         │                    │
│         │ x(t)                    │ u(t)               │
│         │                         │                    │
│         ▼                         ▲                    │
│  ┌──────────────────────────────────────┐             │
│  │   GVSoCMPCController (Wrapper)       │             │
│  │   - Llama gapy como subproceso       │             │
│  │   - Parsea output                    │             │
│  └──────────────┬────────────────────────┘            │
└─────────────────┼──────────────────────────────────────┘
                  │
                  │ subprocess call
                  ▼
┌─────────────────────────────────────────────────────────┐
│              GVSoC (RISC-V Simulator)                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  PULP-open Virtual Platform                      │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  mpc_acc_controller.c (RISC-V Binary)     │  │  │
│  │  │  - Recibe x, w                             │  │  │
│  │  │  - Optimización MPC                        │  │  │
│  │  │  - Devuelve u                              │  │  │
│  │  │  - Output via STDOUT (0x1A10F000)          │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura del Repositorio

```
riscv_bridge/
│
├── README.md                       # Este archivo
│
├── mpc_acc_controller.c            # ⭐ Controlador MPC en C
├── start.S                         # Código de arranque RISC-V
├── riscv.ld                        # Linker script PULP-open
├── mpc_acc.elf                     # Binary compilado
│
├── run_sharc_with_gvsoc.py         # ⭐ Simulación closed-loop completa
├── test_mpc_controller.py          # Test standalone del controlador
├── quick_test.py                   # Test rápido (5 pasos)
│
├── spiflash.bin                    # Flash image (requerido por GVSoC)
├── hyperflash.bin                  # HyperFlash image (requerido por GVSoC)
├── simulation_results.json         # Resultados guardados
│
└── .venv/                          # Python virtual environment
```

---

## 🚀 Uso Rápido

### 1. Compilar el Controlador

```bash
cd ~/riscv_bridge

/opt/riscv/bin/riscv32-unknown-elf-gcc \
  -march=rv32imc -mabi=ilp32 -O2 -nostartfiles \
  -Triscv.ld start.S mpc_acc_controller.c \
  -o mpc_acc.elf
```

### 2. Configurar el Entorno

**IMPORTANTE:** Antes de ejecutar cualquier prueba, configurar el PATH:

```bash
cd ~/riscv_bridge
source .venv/bin/activate
export PATH=~/PULP/pulp-sdk/install/workstation/bin:$PATH
```

### 3. Test Standalone del Controlador

```bash
# Test simple con el wrapper Python
python test_mpc_controller.py
```

**Output esperado:**
```
=== Testing GVSoC MPC Controller ===

Input state:
  k = 0
  t = 0.0 s
  x = [pos=0.0m, headway=60.0m, vel=15.0m/s]
  w = [v_front=11.0m/s, const=1.0]

MPC_START
U=0.00,3000.00
COST=999.00
ITER=13
CYCLES=0
STATUS=OPTIMAL
MPC_DONE
```

### 4. Simulación Closed-Loop Completa

```bash
# Test rápido (5 pasos, ~2 minutos)
python quick_test.py

# Simulación completa (30 pasos = 6 segundos simulados, ~10 minutos)
python run_sharc_with_gvsoc.py
```

**Output:**
```
Step   0 (t=  0.0s): v= 15.0 m/s, h= 60.0m, v_f= 11.0 m/s | u=[   0.0, 3000.0] N | cost=   999.0
Step   1 (t=  0.2s): v= 14.7 m/s, h= 59.4m, v_f= 11.3 m/s | u=[   0.0, 2800.0] N | cost=   999.0
...
```

---

## 🔬 Detalles Técnicos

### Controlador MPC (mpc_acc_controller.c)

**Modelo del Sistema:**
- **Estados (x)**: `[posición, headway, velocidad]`
- **Controles (u)**: `[F_accel, F_brake]` (Newtons)
- **Entradas exógenas (w)**: `[v_front, constante]`

**Dinámica ACC:**
```c
dp/dt = v
dh/dt = v_front - v
dv/dt = (F_accel - F_brake - F_friction) / mass

F_friction = β + γ*v²
  β = 339.1329 N
  γ = 0.77 N·s²/m²
  mass = 2044 kg
```

**Parámetros:**
- Prediction horizon: 5 pasos
- Sample time: 0.2 segundos
- Desired velocity: 15 m/s
- Minimum safe distance: 6 m

**Optimización:**
1. **Grid Search** (7×7): Explora espacio de control
   - Solo aceleración O frenado (nunca ambos)
   - Búsqueda adaptativa según velocidad relativa
2. **Gradient Descent** (3 iteraciones): Refinamiento
3. **Heurística de seguridad**: Si optimización falla, frena proporcionalmente

**Función de Costo:**
```c
J = 100000*(v - v_front)²          // Prioridad: igualar velocidades
  + 100*(v - v_des)²               // Tracking velocidad deseada
  + 50000*(3 - time_to_collision)² // Seguridad temporal
  + 10000*max(0, d_safe - h)²      // Headway mínimo
  + 0.001*(F_accel² + F_brake²)    // Esfuerzo de control
  + 0.1*(ΔF_accel² + ΔF_brake²)    // Suavidad
```

### Comunicación STDOUT

El controlador usa el periférico STDOUT de PULP en `0x1A10F000`:

```c
void stdout_putc(char c) {
    volatile uint32_t *putc_reg = (volatile uint32_t *)(0x1A10F000);
    *putc_reg = (uint32_t)c;
}
```

**Formato de salida:**
```
MPC_START
U=<F_accel>,<F_brake>
COST=<value>
ITER=<count>
CYCLES=<count>
STATUS=<OPTIMAL|OTHER>
MPC_DONE
```

### Integración Python (run_sharc_with_gvsoc.py)

**Clase principal:** `GVSoCMPCController`
- Ejecuta `gapy` como subproceso
- Timeout de 120 segundos por llamada
- Parsea output con expresiones regulares
- Calcula delay computacional: `t_delay = cycles / freq`

**Clase dinámica:** `ACCDynamics`
- Integración Euler forward
- Aplica restricciones de velocidad [0, 20] m/s
- Modelo de fricción no lineal

**Loop de simulación:**
```python
for k in range(n_steps):
    t = k * dt
    v_front = compute_v_front(t)  # Velocidad del líder
    w = [v_front, 1.0]
    
    u, metadata = controller.compute_control(k, t, x, w)
    
    x_new = dynamics.integrate_euler(t, x, u, w, dt)
```

---

## 📊 Resultados

### Ejemplo de Ejecución

**Condiciones iniciales:**
- Ego: 15 m/s, headway 60m
- Líder: 11 m/s (variable sinusoidal)

**Comportamiento:**
1. **t=0s**: Detecta que ego va más rápido → Frena 3000N
2. **t=0.2-1.0s**: Frena progresivamente, velocidades convergen
3. **t>1.0s**: Mantiene distancia segura

**Métricas típicas:**
- Iteraciones: ~13 por control
- Delay computacional: ~3 ms (estimado)
- Headway mínimo: >55m (seguro)
- Desaceleración máxima: -1.72 m/s² (confortable)

### Archivos de Salida

**simulation_results.json:**
```json
{
  "time": [0.0, 0.2, 0.4, ...],
  "velocity": [15.0, 14.7, 14.3, ...],
  "headway": [60.0, 59.4, 58.9, ...],
  "F_accel": [0.0, 0.0, 0.0, ...],
  "F_brake": [3000.0, 2800.0, 2600.0, ...],
  "cost": [999.0, 999.0, 999.0, ...],
  "iterations": [13, 13, 13, ...],
  "cycles": [0, 0, 0, ...],
  "delay": [0.003, 0.003, 0.003, ...]
}
```

---

## 🛠️ Dependencias

### Software Requerido

1. **RISC-V Toolchain:**
   - `/opt/riscv/bin/riscv32-unknown-elf-gcc`
   - Target: rv32imc

2. **PULP SDK:**
   - `~/PULP/pulp-sdk/install/workstation/`
   - GVSoC launcher y modelos

3. **Python 3.12+:**
   - numpy
   - subprocess, re, json (stdlib)

### Instalación de Dependencias

```bash
# Crear virtual environment
cd ~/riscv_bridge
python3 -m venv .venv
source .venv/bin/activate
pip install numpy
```

---

## 🔧 Desarrollo

### Modificar el Controlador

1. Editar `mpc_acc_controller.c`
2. Recompilar: `make` o comando gcc directo
3. Probar: `python quick_test.py`

### Ajustar Parámetros

**En mpc_acc_controller.c:**
```c
#define GRID_SIZE 7              // Resolución búsqueda
#define GRADIENT_ITER 3          // Iteraciones refinamiento
#define PREDICTION_HORIZON 5     // Horizonte predicción
```

**En run_sharc_with_gvsoc.py:**
```python
results = run_simulation(
    n_steps=30,    # Número de pasos
    dt=0.2,        # Tiempo de muestreo
    save_results=True
)
```

### Debugging

**Ver trace de ejecución:**
```bash
gapy ... --trace insn run
```

**Verificar compilación:**
```bash
/opt/riscv/bin/riscv32-unknown-elf-objdump -d mpc_acc.elf | less
```

**Logs de GVSoC:**
```bash
cat ~/riscv_bridge/gvsoc.log
```

---

## ⚡ Performance

### Tiempos de Ejecución

| Componente | Tiempo |
|------------|--------|
| Compilación | ~1 segundo |
| GVSoC por llamada | ~20 segundos |
| Simulación 5 pasos | ~2 minutos |
| Simulación 30 pasos | ~10 minutos |

### Optimizaciones Futuras

1. **Reducir grid search**: 7×7 → 5×5 (más rápido)
2. **Cache de resultados**: Reusar soluciones similares
3. **Parallel GVSoC**: Múltiples instancias
4. **Contador de ciclos real**: Habilitar rdcycle en PULP

---

## 📚 Referencias

### Archivos Clave

- **PULP STDOUT**: `PULP/pulp-sdk/install/workstation/generators/.../memory_map.h`
- **PULP Memory**: ROM 0x1c000000, RAM 0x1c010000
- **GVSoC Config**: Auto-generado en `work-dir/gvsoc_config.json`

### SHARC Original

El sistema SHARC original está en `~/sharc_original/` con implementación C++ completa usando OSQP. Este proyecto es una versión simplificada optimizada para RISC-V.

---

## 🎯 Estado del Proyecto

### ✅ Completado

- [x] Controlador MPC funcional en C
- [x] Compilación para RISC-V
- [x] Ejecución en GVSoC
- [x] Comunicación via STDOUT
- [x] Integración Python wrapper
- [x] Simulación closed-loop
- [x] Optimización híbrida
- [x] Heurística de seguridad
- [x] Visualización de resultados

### 🚧 Pendiente

- [ ] Medición real de ciclos CPU (actualmente placeholder)
- [ ] Soporte para argumentos de línea de comando
- [ ] Comparación con OSQP baseline
- [ ] Optimizaciones de velocidad
- [ ] Múltiples escenarios de test

---

## 📞 Contacto

Para preguntas o issues relacionados con este proyecto, consultar la documentación de PULP SDK y GVSoC en:
- https://github.com/pulp-platform/pulp-sdk
- https://github.com/gvsoc/gvsoc

---

**Última actualización:** 30 Enero 2026
