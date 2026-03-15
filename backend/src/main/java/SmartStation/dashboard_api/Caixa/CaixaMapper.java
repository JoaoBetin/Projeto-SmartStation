package SmartStation.dashboard_api.Caixa;

import SmartStation.dashboard_api.Sessao.SessaoModel;
import org.springframework.stereotype.Component;

@Component
public class CaixaMapper {

    public CaixaDTO toDTO(CaixaModel model){
        if(model == null){
            return null;
        }

        CaixaDTO dto = new CaixaDTO();

        dto.setId(model.getId());

        if(model.getSessaoModel() != null){
            dto.setSessaoId(model.getSessaoModel().getId());
        }

        dto.setInicio_deteccao(model.getInicio_deteccao());
        dto.setFim_deteccao(model.getFim_deteccao());
        dto.setTempo_detectado(model.getTempo_detectado());

        return dto;
    }

    public CaixaModel toEntity(CaixaDTO dto){
        if(dto == null){
            return null;
        }

        CaixaModel model = new CaixaModel();

        model.setId(dto.getId());

        if(dto.getSessaoId() != null){
            SessaoModel sessao = new SessaoModel();
            sessao.setId(dto.getSessaoId());
            model.setSessaoModel(sessao);
        }

        model.setInicio_deteccao(dto.getInicio_deteccao());
        model.setFim_deteccao(dto.getFim_deteccao());
        model.setTempo_detectado(dto.getTempo_detectado());

        return model;
    }
}