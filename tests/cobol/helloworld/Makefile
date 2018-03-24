NAME := helloworld
SRC  := ${NAME}.cob
COBC := cobc
OPTS := -x

build: ${NAME}.cob
	${COBC} -x $<

%.o: %.cob
	${COBC} -c $<

run: build
	./${NAME}

clean:
	rm -f ${NAME} ${NAME}.so ${NAME}.o
