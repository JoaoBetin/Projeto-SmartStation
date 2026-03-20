package SmartStation.dashboard_api.Funcionario;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/funcionario")
public class FuncionarioController {
    private final FuncionarioService funcionarioService;

    public FuncionarioController(FuncionarioService funcionarioService) {
        this.funcionarioService = funcionarioService;
    }

    @GetMapping("/listar")
    public ResponseEntity<?> listarTodos(){
        List<FuncionarioDTO> funcionarioDTOList = funcionarioService.listarFuncionarios();
        if(!funcionarioDTOList.isEmpty()){
            return ResponseEntity.ok(funcionarioDTOList);
        }
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body("Nenhum funcionario registrado");
    }

    @GetMapping("/listarID/{id}")
    public ResponseEntity<?> listarID(@PathVariable Long id){
        FuncionarioDTO funcionarioDTO = funcionarioService.listarFuncionariosID(id);

        if(funcionarioDTO != null){
            return ResponseEntity.ok(funcionarioDTO);
        }
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body("Funcionario nao encontrado");
    }

    @GetMapping("/listarAtivos")
    public ResponseEntity<?> listarAtivos(){
        List<FuncionarioDTO> funcionarioDTOList = funcionarioService.listarAtivos();
        if(!funcionarioDTOList.isEmpty()){
            return ResponseEntity.ok(funcionarioDTOList);
        }
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body("Nenhum funcionario ativo");
    }

    @GetMapping("/verificarAtivo/{id}")
    public ResponseEntity<?> verificarAtivo(@PathVariable Long id){
        return ResponseEntity.ok(funcionarioService.verificarAtivo(id));
    }

    @PostMapping("/criar")
    public ResponseEntity<FuncionarioDTO> criarFuncionario(@RequestBody FuncionarioDTO funcionarioDTO){
        FuncionarioDTO funcionario = funcionarioService.criarFuncionario(funcionarioDTO);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(funcionario);

    }

    @DeleteMapping("/deletar/{id}")
    public ResponseEntity<?> deletarFuncionario(@PathVariable Long id){
        FuncionarioDTO funcionarioDTO = funcionarioService.listarFuncionariosID(id);

        if(funcionarioDTO != null){
            funcionarioService.deletarFuncionario(id);
            return ResponseEntity.ok(id + " foi deletado");
        }

        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(id + " nao foi encontrado");
    }

    @PatchMapping("/alterar/{id}")
    public ResponseEntity<?> alterarFuncionario(@PathVariable Long id, @RequestBody FuncionarioDTO funcionarioUser){
        FuncionarioDTO funcionarioDTO = funcionarioService.alterarFuncionario(id, funcionarioUser);
        return ResponseEntity.ok(funcionarioDTO);
    }
}
