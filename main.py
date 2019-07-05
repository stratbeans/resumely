import sys
from extract import SkillExtractor 

filename = sys.argv[1]
skillExtractor = SkillExtractor()
skillExtractor.parse(filename);
skillExtractor.extractSkills()
