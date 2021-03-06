# -*- coding: utf-8 -*-
'''
Created on 08.11.2014

@author: Simon Gwerder
'''

from rdflib.namespace import SKOS
from semnet.osmsemanticnet import OSMSemanticNet
from thesaurus.rdfgraph import RDFGraph
from utilities.configloader import ConfigLoader

class MapOSMSemanticNet:

    def __init__(self, tagFinderRDF, osnSemNetFilePath=None):

        if tagFinderRDF is None: return
        osnSemNetRDF = None
        if osnSemNetFilePath is not None:
            #print('Loading OSN graph')
            osnSemNetRDF = RDFGraph(osnSemNetFilePath)
        osn = OSMSemanticNet(osnSemNetRDF) # if osnSemNetRDF is None it will check the web graph

        termSchemeName = ConfigLoader().getThesaurusString('TERM_SCHEME_NAME')

        count = 0
        for subject, predicate, obj in tagFinderRDF.graph:
            if not osn.baseUrl in subject and not termSchemeName in subject: # check if some osn matches have been added already
                osnConcept = None
                if predicate == SKOS.prefLabel:
                    count = count + 1
                    if '=' in str(obj):
                        splitArray = str(obj).split('=')
                        osnConcept = osn.getConcept(splitArray[0], splitArray[1])
                    else:
                        osnConcept = osn.getConcept(str(obj))

                if osnConcept:
                    tagFinderRDF.addRelatedMatch(subject, osnConcept)
                    #print(str(count) + ' : Added Matching Concept Mapping from: ' + subject + '\t\t\tto: ' + osnConcept)

        #tagFinderRDF.serialize(tagFinderRDF.filePath)






