NAME := namespace_exer
OPTS := -x -v
COBC := cobc

run: build
	./${NAME}.exe

build: ${NAME}.cob clean
	${COBC} ${OPTS} -o ${NAME}.exe $<

clean:
	rm -f ${NAME}.exe

