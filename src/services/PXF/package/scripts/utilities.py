from glob import glob
import os

candiates = [
"/usr/lib/jvm/java-6-sun",
"/usr/lib/jvm/java-1.6.0-sun-1.6.0.*/jre/",
"/usr/lib/jvm/java-1.6.0-sun-1.6.0.*",
"/usr/lib/jvm/j2sdk1.6-oracle",
"/usr/lib/jvm/j2sdk1.6-oracle/jre",
"/usr/lib/j2sdk1.6-sun",
"/usr/java/jdk1.6*",
"/usr/java/jre1.6*",
"/Library/Java/Home",
"/usr/java/default",
"/usr/lib/jvm/default-java",
"/usr/lib/jvm/java-openjdk",
"/usr/lib/jvm/jre-openjdk",
"/usr/lib/jvm/java-1.7.0-openjdk*",
"/usr/lib/jvm/java-7-openjdk*",
"/usr/lib/jvm/java-7-oracle*",
"/usr/lib/jvm/java-1.6.0-openjdk",
"/usr/lib/jvm/java-1.6.0-openjdk-*",
"/usr/lib/jvm/jre-1.6.0-openjdk*",
"/usr/jdk64/jdk1.7.0_*",
]

def detect_java_home():
  java_home = os.environ.get('JAVA_HOME')
  if java_home:
    return java_home
  else:
    for candiate in candiates:
      possiblePaths = glob(candiate)
      if possiblePaths:
        for possiblePath in possiblePaths:
          java_path = os.path.join(possiblePath, "bin/java")
          if os.path.isfile(java_path):
            return possiblePath
  return None
