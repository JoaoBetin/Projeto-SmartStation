package SmartStation.dashboard_api.Caixa;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/caixa")
public class CaixaController {

    private final CaixaService caixaService;

    public CaixaController(CaixaService caixaService) {
        this.caixaService = caixaService;
    }

    @GetMapping("/listar")
    public ResponseEntity<?> listarTodas(){

        List<CaixaDTO> caixas = caixaService.listarCaixas();

        if(!caixas.isEmpty()){
            return ResponseEntity.ok(caixas);
        }

        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body("Nenhuma caixa registrada");
    }

    @GetMapping("/listar/{id}")
    public ResponseEntity<?> listarID(@PathVariable Long id){

        CaixaDTO caixa = caixaService.listarCaixaID(id);

        if(caixa != null){
            return ResponseEntity.ok(caixa);
        }

        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body("Caixa nao encontrada!");
    }

    @PostMapping("/criar")
    public ResponseEntity<CaixaDTO> criarCaixa(@RequestBody CaixaDTO dto){

        CaixaDTO caixa = caixaService.criarCaixa(dto);

        return ResponseEntity.status(HttpStatus.CREATED)
                .body(caixa);
    }

    @PostMapping("/detectada")
    public ResponseEntity<CaixaDTO> caixaDetectada(@RequestBody CaixaDTO dto){

        CaixaDTO caixa = caixaService.registrarDeteccao(dto);

        return ResponseEntity.status(HttpStatus.CREATED).body(caixa);
    }

    @DeleteMapping("/deletar/{id}")
    public ResponseEntity<?> deletarCaixa(@PathVariable Long id){

        CaixaDTO caixa = caixaService.listarCaixaID(id);

        if(caixa != null){
            caixaService.deletarCaixa(id);
            return ResponseEntity.ok("Caixa removida");
        }

        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body("Caixa nao encontrada!");
    }

    @PatchMapping("/alterar/{id}")
    public ResponseEntity<?> alterarCaixa(@PathVariable Long id, @RequestBody CaixaDTO dto){

        CaixaDTO caixa = caixaService.alterarCaixa(id, dto);

        return ResponseEntity.ok(caixa);
    }
}