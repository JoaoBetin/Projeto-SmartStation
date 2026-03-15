package SmartStation.dashboard_api.Sessao;

import org.springframework.stereotype.Component;

@Component
public class SessaoMapper {

    public SessaoDTO toDTO(SessaoModel model) {
        if (model == null) {
            return null;
        }

        SessaoDTO dto = new SessaoDTO();

        dto.setId(model.getId());
        dto.setFuncionarioModel(model.getFuncionarioModel());
        dto.setData(model.getData());
        dto.setHora_inicio(model.getHora_inicio());
        dto.setHora_fim(model.getHora_fim());
        dto.setTempo_ocioso(model.getTempo_ocioso());
        dto.setTotal_caixas(model.getTotal_caixas());

        return dto;
    }

    public SessaoModel toEntity(SessaoDTO dto) {
        if (dto == null) {
            return null;
        }

        SessaoModel model = new SessaoModel();

        model.setId(dto.getId());
        model.setFuncionarioModel(dto.getFuncionarioModel());
        model.setData(dto.getData());
        model.setHora_inicio(dto.getHora_inicio());
        model.setHora_fim(dto.getHora_fim());
        model.setTempo_ocioso(dto.getTempo_ocioso());
        model.setTotal_caixas(dto.getTotal_caixas());

        return model;
    }
}
