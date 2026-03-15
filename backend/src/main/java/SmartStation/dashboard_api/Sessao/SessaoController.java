package SmartStation.dashboard_api.Sessao;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/sessao")
public class SessaoController {
    private final SessaoService sessaoService;

    public SessaoController(SessaoService sessaoService) {
        this.sessaoService = sessaoService;
    }

    @GetMapping("/listar")
    private ResponseEntity<?> listarTodos(){
        List<SessaoDTO> sessaoDTOList = sessaoService.listarSessao();

        if(!sessaoDTOList.isEmpty()){
            return ResponseEntity.ok(sessaoDTOList);
        }
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body("Nenhuma sessao registrada");
    }

    @GetMapping("/listar/{id}")
    public ResponseEntity<?> listarID(@PathVariable Long id){
        SessaoDTO sessaoDTO = sessaoService.listarSessaoID(id);

        if(sessaoDTO != null){
            return ResponseEntity.ok(sessaoDTO);
        }
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body("Sessao nao encontrada!");
    }

    @PostMapping("/criar")
    public ResponseEntity<SessaoDTO> criarSessao(@RequestBody SessaoDTO dto){
        SessaoDTO sessao = sessaoService.criarSessao(dto);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(sessao);
    }

    @DeleteMapping("/deletar/{id}")
    public ResponseEntity<?> deletarSessao(@PathVariable Long id){
        SessaoDTO sessaoDTO = sessaoService.listarSessaoID(id);

        if(sessaoDTO != null){
            sessaoService.deletarSessao(id);
            return ResponseEntity.ok(id + " foi removido!");
        }
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body("Sessao nao encontrada!");
    }

    @PatchMapping("/alterar/{id}")
    public ResponseEntity<?> alterarSessao(@PathVariable Long id, @RequestBody SessaoDTO sessaoUser){
        SessaoDTO sessaoDTO = sessaoService.alterarSessao(id, sessaoUser);
        return ResponseEntity.ok(sessaoDTO);
    }
}
