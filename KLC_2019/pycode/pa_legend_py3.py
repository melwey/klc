# try to convert to python 3
layer = iface.activeLayer()
# create a new rule-based renderer
symbol = QgsSymbol.defaultSymbol(layer.geometryType())
renderer = QgsRuleBasedRenderer(symbol)
root_rule = renderer.rootRule()

def rule_based_style(layer, renderer, label, expression, color):
    rule = root_rule.children()[0].clone()
    rule.setLabel(label)
    rule.setFilterExpression(expression)    
    rule.symbol().symbolLayer(0).setStrokeColor(QColor(color))
    rule.symbol().symbolLayer(0).setColor(QColor(int(color[1:3], 16), int(color[3:5], 16), int(color[5:7],16), 192))
#    rule.symbol().symbolLayer(0).create({
#        'color':str((int(color[1:3], 16), int(color[3:5], 16), int(color[5:7],16), 192)), 
#        'outline_color': color
#        })
    root_rule.appendChild(rule)
    
# simpleFill
simpleFillLayer = QgsSimpleFillSymbolLayer.create({'outline_width':'0.5', 'color_alpha':'0.75'})
renderer.symbols(QgsRenderContext())[0].changeSymbolLayer(0, simpleFillLayer)
#label= 'IUCN Cat. Ia'; expression = '\"IUCN_CAT\" = \'Ia\' '; color =  '#006400'
rule_based_style(layer, renderer, 'IUCN Cat. Ia', '\"IUCN_CAT\" = \'Ia\' ', '#006400')
rule_based_style(layer, renderer, 'IUCN Cat. Ib', '\"IUCN_CAT\" = \'Ib\' ', '#006400')
#label= 'IUCN Cat. II'; expression='\"IUCN_CAT\" = \'II\' '; color = '#008000'
rule_based_style(layer, renderer, 'IUCN Cat. II', '\"IUCN_CAT\" = \'II\' ', '#008000')
rule_based_style(layer, renderer, 'IUCN Cat. III', '\"IUCN_CAT\" = \'III\' ', '#228B22')
rule_based_style(layer, renderer, 'IUCN Cat. IV', '\"IUCN_CAT\" = \'IV\' ', '#2E8B57')
rule_based_style(layer, renderer, 'IUCN Cat. V', '\"IUCN_CAT\" = \'V\' ', '#3CB371')
rule_based_style(layer, renderer, 'IUCN Cat. VI', '\"IUCN_CAT\" = \'VI\' ', '#90EE90')
rule_based_style(layer, renderer, 'Other protected area', '\"IUCN_CAT\" IN (\'Not Applicable\', \'Not Reported\')  AND "STATUS" = \'Designated\' AND "DESIG_TYPE" = \'National\' ', '#32CD32')

# line pattern
linePatternLayer = QgsLinePatternFillSymbolLayer.create(
    {'angle':'45', 
    'distance':'2', 
    'distance_unit':'MM',
    'line_width':'0.26'})
renderer.symbols(QgsRenderContext())[0].changeSymbolLayer(0, linePatternLayer)
rule_based_style(layer, renderer, 'Proposed', ' "STATUS" = \'Proposed\' ', '#6B8E23')
rule_based_style(layer, renderer, 'International designation', ' "DESIG_TYPE" = \'International\' ', '#DC143C')


# delete the default rule
root_rule.removeChildAt(0)
# render and refresh
layer.setRenderer(renderer)
layer.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(layer.id())

## refine rules using categories
#
#fn = 'WDPAID'
#for rule in root_rule.children():
#    categs = []
#    # index of field fn in layer
#    idx = layer.dataProvider().fieldNameIndex(fn)
#    # find unique values
#    vals = set()
#    expression = rule.filterExpression()
#    for feature in layer.dataProvider().getFeatures(QgsFeatureRequest().setFilterExpression(expression)):
#        a = feature.attributes()[idx]
#        vals.add(a)
#    
#    for val in list(vals):
#        # create renderer object
#        categ = QgsRendererCategory(val, QgsFillSymbol().createSimple(
#        {'color':'#FFFFFFFF',
#        'style':'no',
#        'outline_color':'#FFFFFFFF', 
#        'outline_style':'no'}
#        ), str(val))
#        # entry for the list of category items
#        categs.append(categ)
#    
#    # create rendered object
#    q = QgsCategorizedSymbolRenderer(fn, categs)
#    p = renderer.refineRuleCategories(rule, q)
#    
## delete rule if it has no children
#n = len(root_rule.children())
#i=0
#while i<n:
#    subrule = root_rule.children()[i].children()
#    if len(subrule) < 1:
#        root_rule.removeChildAt(i)
#        n = len(root_rule.children())
#    else:
#        i = i+1 
#
## render and refresh
#layer.setRenderer(renderer)
#layer.triggerRepaint()
#iface.layerTreeView().refreshLayerSymbology(layer.id())
#
## change labels
#children = renderer.rootRule().children()
fieldName1 = "WDPAID"
fieldName2 = "NAME"
#
#for child in children: # Iterate through groups
#    if child.filter():
#        feat = next(layer.getFeatures(QgsFeatureRequest(child.filter())), None)
#        if feat:
#            for subChild in child.children(): # Iterate through subgroups
#                if subChild.filter():
#                    feat = next(layer.getFeatures(QgsFeatureRequest(subChild.filter())), None)
#                    if feat:
#                        subChild.setLabel( '{:g}'.format(feat.attribute(fieldName1)) + ": " + feat.attribute(fieldName2) )
#iface.layerTreeView().refreshLayerSymbology(layer.id())
#
## rule based feature labelling
#layer.setCustomProperty("labeling/fieldName", fieldName2)
#layer.setCustomProperty("labeling/placement", QgsPalLayerSettings.Horizontal)
#layer.setCustomProperty("labeling/predefinedPointPosition", QgsPalLayerSettings.BottomRight)
#layer.setCustomProperty("labeling/fontSize","7" )
#layer.setCustomProperty("labeling/bufferDraw", True)
#layer.setCustomProperty("labeling/enabled", True )
#layer.triggerRepaint()
## 