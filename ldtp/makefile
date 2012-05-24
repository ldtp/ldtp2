.SUFFIXES: .java .class
.java.class:
	javac $<

SOURCES = \
	Ldtp.java \
	LdtpExecutionError.java

default: Ldtp.class LdtpExecutionError.class

doc: $(SOURCES)
	javadoc $(SOURCES)

test: $(CLASSES)
	java Knight 1 2

clean:
	$(RM) *.class *~ *.html *.css package-list
