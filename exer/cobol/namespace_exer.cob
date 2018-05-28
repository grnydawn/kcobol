      * Cobol Namespace Exercise

       ID DIVISION.
       PROGRAM-ID. NAMESPACE.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-1.
           02  WS-2 PIC 9(2).
       01  WX-1.
           02  WX-2 PIC 9(2).
       PROCEDURE DIVISION.
       TEST-1 SECTION.
       MOVE 1 TO WS-1
       MOVE 2 TO WS-2
       DISPLAY "WS-1 = " WS-1.
       DISPLAY "WS-2 = " WS-2.
       DISPLAY "WS-2 OF WS-1 = " WS-2 OF WS-1.

