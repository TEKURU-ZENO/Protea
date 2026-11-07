"""Model serialization and SBML / JSON format exporter and importer."""

import json
from typing import Any, Dict
from ai.cellular_simulation.schema import SimulationModel, Species, Reaction, Parameter


class ArtifactManager:
    """Exports and imports biological models to/from JSON and standardized SBML-compatible structures."""

    @staticmethod
    def export_json(model: SimulationModel) -> str:
        """Export model as formatted JSON string."""
        return json.dumps(model.to_dict(), indent=2)

    @staticmethod
    def import_json(json_str: str) -> SimulationModel:
        """Import model from JSON string."""
        data = json.loads(json_str)

        species = {
            s_id: Species(**s_data) for s_id, s_data in data.get("species", {}).items()
        }
        reactions = [
            Reaction(**r_data) for r_data in data.get("reactions", [])
        ]
        parameters = {
            p_id: Parameter(**p_data) for p_id, p_data in data.get("parameters", {}).items()
        }

        return SimulationModel(
            model_id=data["model_id"],
            name=data["name"],
            model_version=data.get("model_version", "1.0.0"),
            model_type=data.get("model_type", "ODE"),
            species=species,
            reactions=reactions,
            parameters=parameters,
            compartments=data.get("compartments", ["cytosol"]),
            metadata=data.get("metadata", {}),
        )

    @staticmethod
    def export_sbml_stub(model: SimulationModel) -> str:
        """Export minimal SBML Level 3 Version 2 XML document."""
        xml = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml.append('<sbml xmlns="http://www.sbml.org/sbml/level3/version2/core" level="3" version="2">')
        xml.append(f'  <model id="{model.model_id}" name="{model.name}">')

        # Compartments
        xml.append('    <listOfCompartments>')
        for c in model.compartments:
            xml.append(f'      <compartment id="{c}" spatialDimensions="3" size="1.0" constant="true"/>')
        xml.append('    </listOfCompartments>')

        # Species
        xml.append('    <listOfSpecies>')
        for s_id, s in model.species.items():
            xml.append(f'      <species id="{s_id}" name="{s.name}" compartment="{s.compartment}" initialConcentration="{s.initial_amount}" boundaryCondition="{str(s.is_constant).lower()}"/>')
        xml.append('    </listOfSpecies>')

        # Parameters
        xml.append('    <listOfParameters>')
        for p_id, p in model.parameters.items():
            xml.append(f'      <parameter id="{p_id}" value="{p.value}" constant="true"/>')
        xml.append('    </listOfParameters>')

        # Reactions
        xml.append('    <listOfReactions>')
        for r in model.reactions:
            rev_str = "true" if r.reversible else "false"
            xml.append(f'      <reaction id="{r.reaction_id}" name="{r.name}" reversible="{rev_str}">')
            if r.reactants:
                xml.append('        <listOfReactants>')
                for reac, coeff in r.reactants.items():
                    xml.append(f'          <speciesReference species="{reac}" stoichiometry="{coeff}" constant="true"/>')
                xml.append('        </listOfReactants>')
            if r.products:
                xml.append('        <listOfProducts>')
                for prod, coeff in r.products.items():
                    xml.append(f'          <speciesReference species="{prod}" stoichiometry="{coeff}" constant="true"/>')
                xml.append('        </listOfProducts>')
            xml.append('      </reaction>')
        xml.append('    </listOfReactions>')

        xml.append('  </model>')
        xml.append('</sbml>')
        return "\n".join(xml)
