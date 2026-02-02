.section .init
.global _start

_start:
    la sp, _stack_top
    call main
    
    # Halt execution with WFI (Wait For Interrupt)
1:
    wfi
    j 1b
