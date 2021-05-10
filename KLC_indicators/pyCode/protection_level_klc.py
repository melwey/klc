"""
Modified from https://github.com/BIOPAMA/protection_analyst model exported with python.
Name : wdpa_zone_processing
Group : wdpa
With QGIS : 31415
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProcessingParameterDefinition
from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsProperty
import processing


class Wdpa_zone_processing(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('inputzones', 'Input zones', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        param = QgsProcessingParameterString('zone_id', 'Field with zones identifier ', multiLine=False, defaultValue='KLC_ID')
        #param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
        self.addParameter(QgsProcessingParameterVectorLayer('inputwdpapoints', 'Input wdpa points', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('inputwdpapolygons', 'Input wdpa polygons', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Result', 'Result', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        param = QgsProcessingParameterString('APIComment', 'API Comment', optional=True, multiLine=False, defaultValue="comment on table klc.api_klc_prot_21_05 is '21_05 - KLC protection level May 2021';")
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
        param = QgsProcessingParameterString('wdpaversionperc', 'Postgres Table Name', multiLine=False, defaultValue='api_klc_prot_21_05')
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(25, model_feedback)
        results = {}
        outputs = {}
        
        # Fix zones
        alg_params = {
            'INPUT': parameters['inputzones'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixZones'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Reproject zones
        alg_params = {
            'INPUT': outputs['FixZones']['OUTPUT'],
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:54009'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectZones'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}
        
        # Fix reprojected zones
        alg_params = {
            'INPUT': outputs['ReprojectZones']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixReprojectZones'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        
        # Reproject layer
        alg_params = {
            'INPUT': parameters['inputwdpapolygons'],
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:54009'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectLayer'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Extracted polygons
        alg_params = {
            'INPUT': outputs['ReprojectLayer']['OUTPUT'],
            'INTERSECT': outputs['ReprojectZones']['OUTPUT'],
            'PREDICATE': [0],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractedPolygons'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Reproject points
        alg_params = {
            'INPUT': parameters['inputwdpapoints'],
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:54009'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectPoints'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Remove the points extraction because PA points might be outside KLC but still intersect when buffered.
#        # Extracted points
#        alg_params = {
#            'INPUT': outputs['ReprojectPoints']['OUTPUT'],
#            'INTERSECT': outputs['ReprojectCountries']['OUTPUT'],
#            'PREDICATE': [0],
#            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
#        }
#        outputs['ExtractedPoints'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
#
#        feedback.setCurrentStep(5)
#        if feedback.isCanceled():
#            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'radius',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': 'sqrt(  \"REP_AREA\"/3.14)',
            'INPUT': outputs['ReprojectPoints']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': QgsProperty.fromExpression('"radius"*1000'),
            'END_CAP_STYLE': 0,
            'INPUT': outputs['FieldCalculator']['OUTPUT'],
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}
        
        # Extract points by expression
        alg_params = {
            'EXPRESSION': 'NOT(\"STATUS\" IN (\'Proposed\', \'Not Reported\')) AND NOT(\"DESIG_ENG\" = \'UNESCO-MAB Biosphere Reserve\') AND (\"REP_AREA\" > 0)',
            'INPUT': outputs['Buffer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractPointsByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Fix BUFFER
        alg_params = {
            'INPUT': outputs['ExtractPointsByExpression']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixBuffer'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}
              
        # Extracted points by location
        alg_params = {
            'INPUT': outputs['FixBuffer']['OUTPUT'],
            'INTERSECT': outputs['ReprojectZones']['OUTPUT'],
            'PREDICATE': [0],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractedBuffer'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}
        
        # Fix geometries BUFFER
        alg_params = {
            'INPUT': outputs['ExtractedBuffer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixExtractedBuffer'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}
                
        # Extract polygons by expression
        alg_params = {
            'EXPRESSION': 'NOT(\"STATUS\"   IN  (\'Proposed\', \'Not Reported\')) AND NOT(\"DESIG_ENG\" = \'UNESCO-MAB Biosphere Reserve\')',
            'INPUT': outputs['ExtractedPolygons']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}


        # Fix EXTRACTED
        alg_params = {
            'INPUT': outputs['ExtractByExpression']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixExtracted'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}
        
        ##### need to intersect to add zone_id to PAs ####

        # Dissolve POLYGONS
        alg_params = {
            #'FIELD': parameters['zone_id'],
            'INPUT': outputs['FixExtracted']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DissolvePolygons'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Dissolve BUFFERED POINTS
        alg_params = {
            #'FIELD': parameters['zone_id'],
            'INPUT': outputs['FixExtractedBuffer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DissolveBufferedPoints'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Merged Protection
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:54009'),
            'LAYERS': [outputs['DissolveBufferedPoints']['OUTPUT'],outputs['DissolvePolygons']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergedProtection'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Fix merged points and polygons
        alg_params = {
            'INPUT': outputs['MergedProtection']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixMergedPointsAndPolygons'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}
        
        # INTERESCT with zones to add zone_id
        alg_params = {
            'INPUT': outputs['FixMergedPointsAndPolygons']['OUTPUT'],
            'OVERLAY': outputs['FixReprojectZones']['OUTPUT'],
            'OVERLAY_FIELDS': [parameters['zone_id']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Intersect'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}
        
        # fix intersection
        alg_params = {
            'INPUT': outputs['Intersect']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixIntersect'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Dissolve protection by zone and PA_DEF
        alg_params = {
            'FIELD': [parameters['zone_id'], 'PA_DEF'],
            'INPUT': outputs['FixIntersect']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DissolveProtection'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}
              
        # select features with PA_DEF = "1"
        alg_params = {
            'EXPRESSION': '\"PA_DEF\" = 1',
            'INPUT': outputs['ExtractedPolygons']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractProtection'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Fix dissolved protection
        alg_params = {
            'INPUT': outputs['ExtractProtection']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixDissolvedProtection'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}


        # Calculate area
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'prot_area_km2',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': ' $area *1e-6',
            'INPUT': outputs['FixDissolvedProtection']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateArea'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}
        
        # Join geometries with attributes
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': parameters['zone_id'],
            'FIELDS_TO_COPY': ['prot_area_km2'],
            'FIELD_2': parameters['zone_id'],
            'INPUT': outputs['ReprojectZones']['OUTPUT'],
            'INPUT_2': outputs['CalculateArea']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinGeometriesWithAttributes'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # Calculate country area
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'zone_area_km2',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': ' $area/1000000',
            'INPUT': outputs['JoinGeometriesWithAttributes']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateCountryArea'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Calculate protection percentage
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'pc_prot',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': '(\"prot_area_km2\"*100)/\"zone_area_km2\"',
            'INPUT': outputs['CalculateCountryArea']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculateProtectionPercentage'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # Reproject layer
        alg_params = {
            'INPUT': outputs['CalculateProtectionPercentage']['OUTPUT'],
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'OUTPUT': parameters['Result']
        }
        outputs['ReprojectLayer'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Result'] = outputs['ReprojectLayer']['OUTPUT']

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # Export to PostgreSQL
        alg_params = {
            'CREATEINDEX': True,
            'DATABASE': 'Biopama_api',
            'DROP_STRING_LENGTH': False,
            'ENCODING': 'UTF-8',
            'FORCE_SINGLEPART': False,
            'GEOMETRY_COLUMN': 'geom',
            'INPUT': outputs['ReprojectLayer']['OUTPUT'],
            'LOWERCASE_NAMES': True,
            'OVERWRITE': False,
            'PRIMARY_KEY': '',
            'SCHEMA': 'klc',
            'TABLENAME': parameters['wdpaversionperc']
        }
        outputs['ExportToPostgresql'] = processing.run('qgis:importintopostgis', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(27)
        if feedback.isCanceled():
            return {}

        # Create API
        alg_params = {
            'DATABASE': 'Biopama_api',
            'SQL': parameters['APIComment']
        }
        outputs['CreateApi'] = processing.run('native:postgisexecutesql', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'wdpa_zone_processing'

    def displayName(self):
        return 'wdpa_zone_processing'

    def group(self):
        return 'wdpa'

    def groupId(self):
        return 'wdpa'

    def createInstance(self):
        return Wdpa_zone_processing()
