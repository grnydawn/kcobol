NAME := des
SRC  := ${NAME}.cob
COBC := cobc
OPTS := -v -std=default -free

build: test${NAME}.o cob${NAME}.o
	${COBC} -x ${OPTS} -o ${NAME}.exe $^

test${NAME}.o: test${NAME}.cob
	${COBC} -x -c ${OPTS} $<

cob${NAME}.o: cob${NAME}.cob
	${COBC} -c ${OPTS} $<

run: build
	./${NAME}.exe

clean:
	rm -f ${NAME}.exe test${NAME}.o cob${NAME}.o
