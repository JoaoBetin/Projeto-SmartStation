package SmartStation.dashboard_api.Controllers;

import SmartStation.dashboard_api.DTOs.LoginRequestDTO;
import SmartStation.dashboard_api.DTOs.LoginResponseDTO;
import SmartStation.dashboard_api.Enums.Cargo;
import SmartStation.dashboard_api.Models.FuncionarioModel;
import SmartStation.dashboard_api.Repositorys.FuncionarioRepository;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;

@CrossOrigin(origins = "*")
@RestController
@RequestMapping("/auth")
public class AuthController {

    private final FuncionarioRepository funcionarioRepository;

    public AuthController(FuncionarioRepository funcionarioRepository) {
        this.funcionarioRepository = funcionarioRepository;
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequestDTO loginRequest) {

        if (loginRequest.getMatricula() == null || loginRequest.getSenha() == null) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body("Matricula e senha sao obrigatorias");
        }

        Optional<FuncionarioModel> funcionarioOpt = funcionarioRepository
                .findAll()
                .stream()
                .filter(f -> f.getMatricula().equals(loginRequest.getMatricula()))
                .findFirst();

        if (funcionarioOpt.isEmpty()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body("Matricula ou senha invalidos");
        }

        FuncionarioModel funcionario = funcionarioOpt.get();

        if (funcionario.getAtivo() == null || !funcionario.getAtivo()) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body("Funcionario inativo");
        }

        // Senha padrão para todos: "smart" + matricula
        // ADMIN também pode usar "admin123"
        String senhaEsperadaPadrao = "smart" + loginRequest.getMatricula();
        boolean isAdmin = Cargo.ADMIN.equals(funcionario.getCargo());

        boolean senhaCorreta = loginRequest.getSenha().equals(senhaEsperadaPadrao)
                || (isAdmin && loginRequest.getSenha().equals("admin123"));

        if (!senhaCorreta) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body("Matricula ou senha invalidos");
        }

        LoginResponseDTO response = new LoginResponseDTO(
                funcionario.getId(),
                funcionario.getNome(),
                funcionario.getMatricula(),
                funcionario.getCargo()
        );

        return ResponseEntity.ok(response);
    }
}
