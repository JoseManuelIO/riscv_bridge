ENTRY(_start)

MEMORY
{
  ROM (rx) : ORIGIN = 0x1c000000, LENGTH = 0x00190000
  RAM (rwx) : ORIGIN = 0x1c010000, LENGTH = 0x00180000
}

SECTIONS
{
  .init : {
    *(.init*)
  } > ROM

  .text : {
    *(.text*)
    *(.rodata*)
  } > ROM

  .data : {
    *(.data*)
  } > RAM AT > ROM

  .bss : {
    *(.bss*)
  } > RAM

  PROVIDE(_stack_top = ORIGIN(RAM) + LENGTH(RAM));

  /DISCARD/ : {
    *(.note.GNU-stack)
    *(.gnu_debuglink)
    *(.gnu.lto_*)
  }
}
