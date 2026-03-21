package SmartStation.dashboard_api.Sessao;

import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class SessaoService {
    SessaoMapper sessaoMapper;
    SessaoRepository sessaoRepository;

    public SessaoService(SessaoMapper sessaoMapper, SessaoRepository sessaoRepository) {
        this.sessaoMapper = sessaoMapper;
        this.sessaoRepository = sessaoRepository;
    }

    // Listar todos
    public List<SessaoDTO> listarSessao(){
        List<SessaoModel> sessaoModelList = sessaoRepository.findAll();

        return sessaoModelList.stream()
                .map(sessaoMapper::toDTO)
                .collect(Collectors.toList());
    }

    // Listar por ID
    public SessaoDTO listarSessaoID(Long id){
        Optional<SessaoModel> sessaoModelOptional = sessaoRepository.findById(id);

        return sessaoModelOptional.map(sessaoMapper::toDTO).orElse(null);
    }

    // Criar
    public SessaoDTO criarSessao(SessaoDTO sessaoDTO){

        SessaoModel sessaoModel = sessaoMapper.toEntity(sessaoDTO);

        SessaoModel sessaoSalva = sessaoRepository.save(sessaoModel);

        return sessaoMapper.toDTO(sessaoSalva);
    }

    // Deletar
    public void deletarSessao(Long id){
        sessaoRepository.deleteById(id);
    }

    // Alterar ID
    public SessaoDTO alterarSessao(Long id, SessaoDTO sessaoDTO){
        SessaoModel sessaoModel = sessaoRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Sessao nao encontrada"));

        if(sessaoDTO.getFuncionarioDTO() != null){
            sessaoModel.setFuncionarioModel(sessaoDTO.getFuncionarioDTO());
        }

        if(sessaoDTO.getData() != null){
            sessaoModel.setData(sessaoDTO.getData());
        }

        if(sessaoDTO.getAtiva() != null){
            sessaoModel.setAtiva(sessaoDTO.getAtiva());
        }

        if(sessaoDTO.getHora_inicio() != null){
            sessaoModel.setHora_inicio(sessaoDTO.getHora_inicio());
        }

        if(sessaoDTO.getHora_fim() != null){
            sessaoModel.setHora_fim(sessaoDTO.getHora_fim());
        }

        if(sessaoDTO.getTempo_ocioso() != null){
            sessaoModel.setTempo_ocioso(sessaoDTO.getTempo_ocioso());
        }

        if(sessaoDTO.getTotal_caixas() != null){
            sessaoModel.setTotal_caixas(sessaoDTO.getTotal_caixas());
        }

        SessaoModel sessaoSalva = sessaoRepository.save(sessaoModel);

        return sessaoMapper.toDTO(sessaoSalva);
    }
}
