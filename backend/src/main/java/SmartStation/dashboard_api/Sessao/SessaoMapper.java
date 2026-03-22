package SmartStation.dashboard_api.Sessao;

import SmartStation.dashboard_api.Funcionario.FuncionarioModel;
import org.springframework.stereotype.Component;

@Component
public class SessaoMapper {

    public SessaoDTO toDTO(SessaoModel model) {
        if (model == null) {
            return null;
        }

        SessaoDTO dto = new SessaoDTO();

        dto.setId(model.getId());
        dto.setFuncionarioID(model.getFuncionarioModel().getId());
        dto.setData(model.getData());
        dto.setHoraInicio(model.getHoraInicio());
        dto.setHoraFim(model.getHoraFim());
        dto.setTempoOcioso(model.getTempoOcioso());
        dto.setTotalCaixas(model.getTotalCaixas());
        dto.setAtiva(model.getAtiva());


        if(model.getFuncionarioModel() != null){
            dto.setFuncionarioID(model.getFuncionarioModel().getId());
        }

        return dto;
    }

    public SessaoModel toEntity(SessaoDTO dto) {
        if (dto == null) {
            return null;
        }

        SessaoModel model = new SessaoModel();

        model.setId(dto.getId());
        model.setData(dto.getData());
        model.setHoraInicio(dto.getHoraInicio());
        model.setHoraFim(dto.getHoraFim());
        model.setTempoOcioso(dto.getTempoOcioso());
        model.setTotalCaixas(dto.getTotalCaixas());
        model.setAtiva(dto.getAtiva());

        if(dto.getFuncionarioID() != null){
            FuncionarioModel funcionarioModel = new FuncionarioModel();
            funcionarioModel.setId(dto.getFuncionarioID());
            model.setFuncionarioModel(funcionarioModel);
        }

        return model;
    }
}
