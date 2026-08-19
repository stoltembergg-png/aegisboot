# AegisBoot — SDD Mestre

> **Princípio:** `Stay upstream-compatible. Ship faster. Validate harder. Diverge minimally.`

| Campo | Valor |
|---|---|
| Versão | 1.0.0 |
| Status | Draft |
| Data | 2026-08-19 |
| Autor | Gabriel Stoltemberg |
| Projeto | AegisBoot — Continuous Fork of OpenCorePkg |
| Upstream | `acidanthera/OpenCorePkg` (`master`) |
| Licença | Apache 2.0 (herdada do upstream) |

---

## 1. Visão

AegisBoot é um **fork gerenciado automaticamente** do OpenCorePkg. Seu único objetivo é manter uma cópia **sempre sincronizada** com o upstream, com validação profunda, revisão automatizada, auto-merge seguro e releases próprias mais frequentes — sem nunca divergir por preferência, sem reescrever o que já funciona, e sem mascarar conflitos.

O fork existe para ser um **espeelho mais rigoroso**, não um substituto. Toda mudança local deve ter justificativa técnica documentada. Todo conflito deve ser resolvido com transparência. Toda release deve ser rastreável ao SHA upstream e ao SHA do fork.

---

## 2. Objetivos

| ID | Objetivo | Prioridade |
|---|---|---|
| O-001 | Manter upstream configurado permanentemente como remoto `origin` | Crítica |
| O-002 | Detectar novos commits upstream em até 15 minutos | Crítica |
| O-003 | Sincronizar mudanças via branch dedicada e PR revisável | Crítica |
| O-004 | Validar profundamente qualquer atualização (build, test, QEMU boot) | Crítica |
| O-005 | Resolver conflitos sem mascarar problemas | Crítica |
| O-006 | Manter patches locais mínimos e documentados | Alta |
| O-007 | Revisar PRs automaticamente (CI + análise estática + diff review) | Alta |
| O-008 | Auto-merge somente com todos os gates satisfeitos | Alta |
| O-009 | Classificar impacto de cada merge (patch/minor/major/infra/critical) | Alta |
| O-010 | Liberar releases próprias quando mudança relevante é integrada | Alta |
| O-011 | Permitir releases mais frequentes que o upstream | Média |
| O-012 | Manter rastreabilidade exata: release ↔ upstream SHA ↔ fork SHA | Crítica |
| O-013 | Produzir SBOM, checksums, provenance e artefatos verificáveis | Alta |
| O-014 | Suportar rollback para release anterior em < 5 minutos | Média |
| O-015 | Operar com mínima supervisão cotidiana | Alta |

---

## 3. Não-Objetivos

| ID | Não-Objetivo | Razão |
|---|---|---|
| NO-001 | Criar um bootloader do zero | O fork herda e mantém o OpenCore existente |
| NO-002 | Substituir progressivamente o OpenCore | O upstream é a base de código permanente |
| NO-003 | Divergir por preferência pessoal | Divergência só por necessidade técnica documentada |
| NO-004 | Modificar comportamento upstream sem necessidade | Mudanças locais exigem RFC e aprovação |
| NO-005 | Fornecer suporte a usuários finais do OpenCore | Este é um fork técnico, não um produto de consumo |
| NO-006 | Manter um Changelog separado do upstream | O Changelog do upstream é a fonte primária; alterações locais são adicionadas |
| NO-007 | Reimplementar features que upstream já providencia | Usar upstream diretamente sempre que possível |

---

## 4. Requisitos Funcionais

### 4.1 Sync Engine

| ID | Requisito | Critério de Aceite |
|---|---|---|
| RF-001 | Remote `origin` sempre aponta para `acidanthera/OpenCorePkg` | `git remote get-url origin` retorna a URL correta |
| RF-002 | Fetch automático de upstream a cada 15 minutos | Cron job executa `git fetch origin` e registra resultado |
| RF-003 | Branch `sync/upstream` criada automaticamente a cada novo commit upstream | Branch existe com HEAD = upstream master |
| RF-004 | PR automático criado quando sync branch tem mudanças | PR criado com título, descrição e diff |
| RF-005 | PR inclui diff completo, impacto e análisis automática | PR body contém diff stats, impact classification, analysis |
| RF-006 | PR Link para commit upstream específico | PR body contém link para o commit upstream |
| RF-007 | Fechamento automático de PRs de sync obsoletos | PRs com sync branch desatualizada são fechados |

### 4.2 Validation Pipeline

| ID | Requisito | Critério de Aceite |
|---|---|---|
| RF-010 | Build multi-plataforma (Linux CLANGPDB, CLANGDWARF, GCC; macOS XCODE5; Windows VS2022) | Todos os builds passam sem erro |
| RF-011 | Análise estática (shellcheck, prospector, Coverity) | Zero warnings novos引入 |
| RF-012 | Lint de Sample.plist e SampleCustom.plist | Plists em formato válido |
| RF-013 | Verificação de AppleModels DataBase | `git status --porcelain` retorna vazio após update_generated.py |
| RF-014 | Build de Docs verificado | Docs buildam sem erro |
| RF-015 | Boot test em QEMU/OVMF (múltiplas configurações) | Boot completa sem panic |
| RF-016 | Verificação de integridade dos artefatos (checksums) | SHA256 de cada artefato verificado contra manifest |
| RF-017 | Verificação de SBOM (Software Bill of Materials) | SBOM gerado e válido para cada build |
| RF-018 | Provenance statement gerado para cada release | SLSA provenance incluído na release |
| RF-019 | Geração de checksums para todos os artefatos | SHA256 e SHA512 gerados para cada arquivo de release |

### 4.3 PR Review Automation

| ID | Requisito | Critério de Aceite |
|---|---|---|
| RF-020 | Review automático via bot analisa diff | Bot comenta resumo no PR |
| RF-021 | Verificação de conflitos não resolvidos | Bot detecta e reporta conflitos ocultos |
| RF-022 | Verificação de patches locais preservados | Bot verifica que patches aplicados continuam presentes |
| RF-023 | Análise de risco por arquivo criticado | Bot identifica arquivos de alto risco modificados |
| RF-024 | Label automática baseada em impacto | PR recebe label de impacto automaticamente |
| RF-025 | Bloqueio de merge se qualquer gate falhar | `require-status-checks` impede merge com status vermelho |

### 4.4 Auto-Merge

| ID | Requisito | Critério de Aceite |
|---|---|---|
| RF-030 | Auto-merge habilitado com branch protection | Branch protection com required reviews = 0 (bot) e required checks |
| RF-031 | Merge só ocorre se todos os checks passam | `gh pr merge` só executa se todos os checks são verdes |
| RF-032 | Merge失败 com qualquer status vermelho | Nenhum merge com checks pendentes ou falhos |
| RF-033 | Squash merge para manter histórico limpo | Merge strategy = squash |
| RF-034 | Commit messagepadronizado no merge | Formato: `sync: merge upstream <sha> (<date>)` |

### 4.5 Release Pipeline

| ID | Requisito | Critério de Aceite |
|---|---|---|
| RF-040 | Release automática quando merge relevante é integrado | Release criada automaticamente após merge classificado como `release-worthy` |
| RF-041 | Semver para releases do fork | Formato: `v<upstream_version>.<fork_patch>` |
| RF-042 | Release notes geradas automaticamente | Release notes incluem diff upstream, patches mantidos, impacto |
| RF-043 | Artefatos verificáveis (checksums + provenance) | Cada release tem SHA256, SHA512, SLSA provenance |
| RF-044 | SBOM gerado para cada release | SBOM em formato CycloneDX ou SPDX |
| RF-045 | Rollback para release anterior documentado | Procedimento de rollback documentado e testado |
| RF-046 | Releases mais frequentes que upstream | Fork pode lançar releases entre releases upstream |
| RF-047 | Rastreabilidade: release ↔ upstream SHA ↔ fork SHA | Cada release referencia SHA upstream e SHA fork |

### 4.6 Patch Stack

| ID | Requisito | Critério de Aceite |
|---|---|---|
| RF-050 | Patches locais mantidos em diretório `Patches/` | Cada patch é arquivo `.patch` aplicável via `git am` |
| RF-051 | Patches mínimos e documentados | Cada patch tem justificativa em commit message |
| RF-052 | Verificação de patches preservados após sync | CI verifica que patches continuam aplicáveis |
| RF-053 | Rebase automático de patches sobre novo upstream | Scripts rebaseam patches e reportam conflitos |
| RF-054 | Patch stack versionada | Versão do patch stack é taggeada |

### 4.7 Conflict Resolution

| ID | Requisito | Critério de Aceite |
|---|---|---|
| RF-060 | Conflitos detectados automaticamente | Sync branch reporta conflitos antes de merge |
| RF-061 | Conflitos não são mascarados | Nenhum force-push ou merge forçado sem resolução manual |
| RF-062 | Resolução de conflitos é auditable | Cada resolução é commit separado com justificativa |
| RF-063 | Conflitos são classificados por tipo | Arquivo de conflito, patch envolvido, impacto |
| RF-064 | Conflitos críticos bloqueiam sync | Conflitos em arquivos de alto risco exigem revisão manual |

---

## 5. Requisitos Não-Funcionais

### 5.1 Performance

| ID | Requisito | Métrica |
|---|---|---|
| RNF-001 | Detectar commits upstream em até 15 minutos | Latência entre commit upstream e detecção |
| RNF-002 | Criar PR de sync em até 5 minutos após detecção | Latência entre detecção e PR creation |
| RNF-003 | Pipeline de validação completa em até 30 minutos | Duração total do CI pipeline |
| RNF-004 | Auto-merge em até 5 minutos após gates passarem | Latência entre gates passarem e merge |

### 5.2 Confiabilidade

| ID | Requisito | Métrica |
|---|---|---|
| RNF-010 | 99.9% de uptime do pipeline de sync | Uptime mensal do cron job |
| RNF-011 | Zero merges com gates falhando | Número de merges com checks vermelhos |
| RNF-012 | Zero releases com artefatos corrompidos | Verificação de checksums em todas as releases |
| RNF-013 | Rollback testado e funcional em < 5 minutos | Tempo para restaurar release anterior |

### 5.3 Segurança

| ID | Requisito | Métrica |
|---|---|---|
| RNF-020 | Nenhum segredo no repositório | Verificação com `gitleaks` ou similar |
| RNF-021 | Branch protection habilitada | `main` protegido contra force push e direct push |
| RNF-022 | Tokens de CI com escopo mínimo | GITHUB_TOKEN com permissões mínimas necessárias |
| RNF-023 | Artefatos assinados quando possível | Assinatura de releases com chave GPG ou Sigstore |
| RNF-024 | SBOM e provenance para cada release | SLSA Level 2+ compliance |

### 5.4 Manutenibilidade

| ID | Requisito | Métrica |
|---|---|---|
| RNF-030 | Documentação atualizada para cada mudança | README e docs atualizados em cada PR |
| RNF-031 | Scripts testados e idempotentes | Scripts passam em `shellcheck` e `bats` |
| RNF-032 | Configuração versionada | Toda config está em código (`.github/`, `config.yaml`) |
| RNF-033 | Zero intervenção manual para sync routine | Nenhum passo manual necessário para sync normal |

---

## 6. Restrições

| ID | Restrição | Razão |
|---|---|---|
| R-001 | Upstream é `acidanthera/OpenCorePkg` master branch | Fonte única de verdade para código base |
| R-002 | Repositório é público (ou deve ser) | Transparência e rastreabilidade |
| R-003 | CI deve rodar em GitHub Actions | Plataforma existente do upstream |
| R-004 | Builds devem ser reprodutíveis | Verificação de integridade |
| R-005 | Nenhum force-push em branches protegidas | Prevenção de perda de histórico |
| R-006 | Merge strategy é squash | Histórico limpo e rastreável |
| R-007 | Patches locais devem ser mínimos | Minimizar superfície de divergência |
| R-008 | Toda mudança local requer justificativa | Auditoria e rastreabilidade |
| R-009 | Releases devem ser semver-compatíveis | Compatibilidade com ecossistema |
| R-010 | SBOM e provenance são obrigatórios para releases | Conformidade de segurança |

---

## 7. Arquitetura de Sync

### 7.1 Fluxo Geral

```
┌─────────────────────────────────────────────────────────────┐
│                    AEGISBOOT SYNC ENGINE                     │
│                                                              │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Upstream  │───▶│ Detection    │───▶│ Sync Branch  │      │
│  │ Monitor   │    │ (15min cron) │    │ Creation     │      │
│  └──────────┘    └──────────────┘    └──────┬───────┘      │
│                                              │               │
│                                              ▼               │
│                                    ┌──────────────┐         │
│                                    │ PR Creation   │         │
│                                    │ (auto)        │         │
│                                    └──────┬───────┘         │
│                                              │               │
│                                              ▼               │
│  ┌──────────────────────────────────────────────────┐       │
│  │              VALIDATION PIPELINE                   │       │
│  │                                                    │       │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │       │
│  │  │ Build  │ │ Static │ │ QEMU   │ │ Patch  │   │       │
│  │  │ Multi  │ │ Analysis│ │ Boot   │ │ Stack  │   │       │
│  │  │ Platf. │ │        │ │ Test   │ │ Verify │   │       │
│  │  └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘   │       │
│  │      │          │          │          │          │       │
│  │      └──────────┴──────────┴──────────┘          │       │
│  │                      │                            │       │
│  │                      ▼                            │       │
│  │              ┌──────────────┐                    │       │
│  │              │ Impact       │                    │       │
│  │              │ Classifier   │                    │       │
│  │              └──────┬───────┘                    │       │
│  └─────────────────────┼────────────────────────────┘       │
│                        │                                     │
│                        ▼                                     │
│              ┌──────────────┐                               │
│              │ Auto-Merge   │                               │
│              │ (all gates   │                               │
│              │  green)      │                               │
│              └──────┬───────┘                               │
│                      │                                       │
│                      ▼                                       │
│  ┌──────────────────────────────────────────────────┐       │
│  │              RELEASE PIPELINE                     │       │
│  │                                                    │       │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │       │
│  │  │ SBOM   │ │ Check- │ │ Prove- │ │ GitHub │   │       │
│  │  │ Generate│ │ sums   │ │ nance  │ │ Release│   │       │
│  │  └────────┘ └────────┘ └────────┘ └────────┘   │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Componentes

| Componente | Responsabilidade | Tecnologia |
|---|---|---|
| Upstream Monitor | Detectar novos commits upstream | GitHub API / `git fetch` via cron |
| Sync Branch Creator | Criar branch `sync/upstream` com commits novos | `git` commands |
| PR Creator | Criar PR com diff, análise e impacto | GitHub API (`gh pr create`) |
| Validation Pipeline | Build, test, análise estática, QEMU boot | GitHub Actions workflows |
| Impact Classifier | Classificar impacto do merge | Análise de diff + regras |
| Auto-Merge Engine | Merge após todos gates passarem | `gh pr merge --auto` + branch protection |
| Release Pipeline | Gerar SBOM, checksums, provenance, release | GitHub Actions + Sigstore |
| Patch Stack Manager | Manter e rebase patches locais | `git am`, scripts customizados |
| Conflict Resolver | Detectar e reportar conflitos | `git merge-tree`, `gh pr` |

---

## 8. Branch Model

### 8.1 Branches Principais

| Branch | Origem | Proteção | Uso |
|---|---|---|---|
| `main` | Fork base | Force push bloqueado, required reviews, required checks | Branch estável do fork |
| `sync/upstream` | Criada automaticamente | Criada e deletada por bot | Branch temporária para sync |
| `patches/<name>` | Manual ou automática | Force push bloqueado | Patches locais persistentes |
| `release/<version>` | Criada na release | Protegida | Branch de release específica |

### 8.2 Fluxo de Branches

```
acidanthera/OpenCorePkg (upstream)
         │
         │ fetch
         ▼
   origin/master (upstream remote)
         │
         │ sync
         ▼
   sync/upstream (temp branch)
         │
         │ PR + validation
         ▼
   main (protected)
         │
         │ release
         ▼
   release/v1.242.0.1 (tagged)
```

### 8.3 Naming Convention

| Tipo | Formato | Exemplo |
|---|---|---|
| Sync branch | `sync/upstream` | `sync/upstream` |
| Patch branch | `patches/<name>` | `patches/ata-timeout-reduction` |
| Release branch | `release/<version>` | `release/v1.242.0.1` |
| Feature branch | `feat/<name>` | `feat/add-xyz-driver` |
| Hotfix branch | `hotfix/<name>` | `hotfix/critical-boot-fix` |

---

## 9. Modelo de PR

### 9.1 PR Types

| Tipo | Trigger | Título | Merge Strategy |
|---|---|---|---|
| Sync | Cron job (15min) | `sync: merge upstream <sha> (<date>)` | Squash |
| Patch | Manual | `patch: <description>` | Squash |
| Hotfix | Incidente | `hotfix: <description>` | Squash |
| Config | Manual | `config: <description>` | Squash |
| Docs | Manual | `docs: <description>` | Squash |

### 9.2 PR Template

```markdown
## Type
[ ] Sync upstream  [ ] Patch  [ ] Hotfix  [ ] Config  [ ] Docs

## Upstream Reference
- Upstream SHA: `<sha>`
- Upstream Commit: <link>
- Upstream Date: <date>

## Changes
- <list of changes>

## Impact Classification
- [ ] None  [ ] Patch  [ ] Minor  [ ] Major  [ ] Critical  [ ] Infrastructure

## Patches Affected
- [ ] None  [ ] Applied: <list>  [ ] Conflict: <list>

## Validation
- [ ] Build (all platforms)
- [ ] Static analysis
- [ ] QEMU boot test
- [ ] Patch stack verification
- [ ] SBOM generation
- [ ] Checksum verification

## Checklist
- [ ] No secrets in diff
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Release notes drafted (if release-worthy)
```

---

## 10. Gates

### 10.1 Required Checks (Branch Protection)

| Check | Workflow | Trigger | Blocking |
|---|---|---|---|
| `build-linux-clangpdb` | `build.yml` | push, PR | Sim |
| `build-linux-clangdwarf` | `build.yml` | push, PR | Sim |
| `build-linux-gcc5` | `build.yml` | push, PR | Sim |
| `build-macos` | `build.yml` | push, PR | Sim |
| `build-windows` | `build.yml` | push, PR | Sim |
| `analyze-shell-scripts` | `analyze.yml` | push, PR | Sim |
| `analyze-python-scripts` | `analyze.yml` | push, PR | Sim |
| `analyze-docs-linux` | `analyze.yml` | push, PR (master only) | Não |
| `analyze-coverity` | `analyze.yml` | push (master only) | Não |
| `qemu-boot-test` | `test.yml` (novo) | push, PR | Sim |
| `patch-stack-verify` | `patches.yml` (novo) | push, PR | Sim |
| `sbom-generate` | `release.yml` (novo) | release | Sim |

### 10.2 Merge Requirements

Para merge em `main`:

1. **Todos os required checks passam** (verde)
2. **Nenhum conflito aberto**
3. **PR aprovado pelo bot de review** (auto-approve se todos gates passam)
4. **Branch protection:** force push bloqueado, direct push bloqueado
5. **Squash merge** com commit message padronizado

### 10.3 Merge Blocks

Merge é **bloqueado** se:

- Qualquer check está vermelho ou pendente
- Conflitos não resolvidos existem
- Patches locais não são mais aplicáveis
- QEMU boot test falha
- SBOM não pode ser gerado
- Checksums não conferem

---

## 11. Testes

### 11.1 Test Matrix

| Teste | Plataforma | Frequência | Critério |
|---|---|---|---|
| Build CLANGPDB | Linux (Docker) | Cada PR | Compila sem erro |
| Build CLANGDWARF | Linux (Docker) | Cada PR | Compila sem erro |
| Build GCC | Linux (Docker) | Cada PR | Compila sem erro |
| Build XCODE5 | macOS | Cada PR | Compila sem erro |
| Build VS2022 | Windows | Cada PR | Compila sem erro |
| Shellcheck | macOS | Cada PR | Zero warnings |
| Prospector | Linux | Cada PR | Zero errors |
| Docs build | Linux | Cada PR (master) | Docs compila |
| Coverity | Linux | Push to master | Zero new defects |
| QEMU/OVMF boot | Linux | Cada PR | Boot completa |
| Patch stack apply | Linux | Cada PR | Todos patches aplicam |
| SBOM generate | Linux | Cada release | SBOM válido |

### 11.2 QEMU Boot Test (novo workflow)

```yaml
# .github/workflows/test.yml
name: Test

on:
  push:
  pull_request:
  workflow_dispatch:

jobs:
  qemu-boot:
    name: QEMU Boot Test
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v6
      - name: Install Dependencies
        run: sudo apt-get update && sudo apt-get install -y qemu-system-x86 ovmf
      - name: Build OC
        run: ./build_oc.tool --skip-package
      - name: Boot Test (OVMF)
        run: |
          # Testar boot com QEMU usando OVMF
          timeout 30 qemu-system-x86_64 \
            -bios /usr/share/ovmf/OVMF.fd \
            -drive file=fat:rw:OpenCorePkg/EFI,format=raw \
            -nographic -serial stdio 2>&1 | tee boot.log
          grep -q "OpenCore" boot.log || (cat boot.log && exit 1)
      - name: Upload boot log
        if: always()
        uses: actions/upload-artifact@v6
        with:
          name: boot-log
          path: boot.log
```

### 11.3 Patch Stack Test (novo workflow)

```yaml
# .github/workflows/patches.yml
name: Patch Stack

on:
  push:
  pull_request:
  workflow_dispatch:

jobs:
  verify-patches:
    name: Verify Patches
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v6
      - name: Verify patches apply cleanly
        run: |
          for patch in Patches/*.patch; do
            echo "Testing: $patch"
            git am --check "$patch" || (echo "FAILED: $patch" && exit 1)
          done
      - name: Verify patches are current
        run: |
          for patch in Patches/*.patch; do
            echo "Checking: $patch"
            git apply --check "$patch" || echo "WARNING: $patch may need rebase"
          done
```

---

## 12. Segurança

### 12.1 Threat Model

| Ameaça | Mitigação | Prioridade |
|---|---|---|
| Commit upstream malicioso | Validação completa antes de merge | Alta |
| Artefatos corrompidos | Checksums (SHA256 + SHA512) em todas as releases | Alta |
| Segredos no repositório | `gitleaks` no CI, branch protection | Alta |
| Merge não autorizado | Branch protection + required checks | Crítica |
| Supply chain attack | SBOM + provenance + dependency scanning | Alta |
| Conflito mascarado | Detecção automática + block merge | Crítica |
| Release com bug | QEMU boot test + rollback capability | Média |
| Token comprometido | Tokens com escopo mínimo, rotação periódica | Média |

### 12.2 Security Gates

| Gate | Ferramenta | Ação em falha |
|---|---|---|
| Secret scanning | `gitleaks` / GitHub secret scanning | Bloqueia PR |
| Dependency scanning | Dependabot / OSV | Alerta + bloqueia se crítico |
| SBOM validation | `syft` / CycloneDX | Bloqueia release |
| Provenance | SLSA generator | Bloqueia release |
| Checksum verification | Script customizado | Bloqueia release |
| Branch protection | GitHub settings | Impede merge direto |

---

## 13. Release Impact

### 13.1 Classificação de Impacto

| Nível | Critério | Exemplo | Ação |
|---|---|---|---|
| `none` | Mudanças em arquivos não-UEFI (docs, scripts) | README update | Merge automático, sem release |
| `patch` | Bug fix, mudança pequena em lib | Fix em OcGuardLib | Merge automático, patch release |
| `minor` | Nova feature, driver, melhoria significativa | Novo driver de rede | Merge automático, minor release |
| `major` | Breaking change, remoção de feature | Remoção de suporte legado | Merge com revisão manual, major release |
| `critical` | Fix de segurança, correção de boot | CVE fix | Merge urgente, release imediata |
| `infrastructure` | Mudança em build system, CI, toolchain | Atualização de compiler | Merge automático, sem release |

### 13.2 Release Criteria

Uma release é criada quando:

1. Merge é classificado como `patch`, `minor`, ou `critical`
2. Todos os gates passam
3. SBOM e checksums são gerados
4. Provenance é criada
5. Release notes são geradas

### 13.3 Semver para Fork

```
v<upstream_version>.<fork_patch>
```

Exemplo:
- Upstream: `v1.0.0` → Fork: `v1.0.0.0`
- Upstream: `v1.0.0` + fork patch: `v1.0.0.1`
- Upstream: `v1.0.1` → Fork: `v1.0.1.0`
- Upstream: `v1.0.1` + fork patch: `v1.0.1.1`

---

## 14. Release Pipeline

### 14.1 Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    RELEASE PIPELINE                          │
│                                                              │
│  1. Merge to main                                           │
│       │                                                      │
│       ▼                                                      │
│  2. Impact Classification                                    │
│       │                                                      │
│       ├─── none/infrastructure → No release                  │
│       │                                                      │
│       ├─── patch/minor/critical → Continue                   │
│       │                                                      │
│       ▼                                                      │
│  3. Generate SBOM (CycloneDX)                               │
│       │                                                      │
│       ▼                                                      │
│  4. Generate Checksums (SHA256 + SHA512)                    │
│       │                                                      │
│       ▼                                                      │
│  5. Generate Provenance (SLSA)                              │
│       │                                                      │
│       ▼                                                      │
│  6. Build Release Artefacts                                 │
│       │                                                      │
│       ▼                                                      │
│  7. Sign Artefacts (Sigstore/GPG)                           │
│       │                                                      │
│       ▼                                                      │
│  8. Create GitHub Release                                   │
│       │                                                      │
│       ▼                                                      │
│  9. Notify (optional)                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 14.2 Release Artefacts

| Artefato | Formato | Descrição |
|---|---|---|
| OpenCore-<version>.zip | ZIP | Binários do OpenCore |
| OpenCorePkg-<version>-sbom.json | CycloneDX JSON | Software Bill of Materials |
| OpenCore-<version>-sha256.txt | Texto | Checksums SHA256 |
| OpenCore-<version>-sha512.txt | Texto | Checksums SHA512 |
| provenance.json | SLSA | Provenance statement |
| release-notes.md | Markdown | Release notes |

---

## 15. Observabilidade

### 15.1 Métricas

| Métrica | Coleta | Alerta |
|---|---|---|
| Sync latency (upstream commit → PR) | Cron log | > 30 minutos |
| Pipeline duration | GitHub Actions | > 45 minutos |
| Pipeline success rate | GitHub Actions | < 95% |
| Time to merge (PR → merge) | GitHub API | > 1 hora |
| Patches rebased successfully | CI log | < 100% |
| QEMU boot test pass rate | CI log | < 100% |
| Releases created | GitHub API | Anomalia |
| Failed merges | GitHub API | > 0 |

### 15.2 Dashboards

| Dashboard | Contato | Frequência |
|---|---|---|
| GitHub Actions | Built-in | Real-time |
| Custom monitoring | Prometheus/Grafana | Diário |
| Health check script | Cron | 15 min |

### 15.3 Health Check Script

```bash
#!/bin/bash
# .github/scripts/health-check.sh
set -euo pipefail

echo "=== AegisBoot Health Check ==="
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Check upstream connectivity
echo -n "Upstream connectivity: "
git ls-remote --heads https://github.com/acidanthera/OpenCorePkg.git >/dev/null 2>&1 && echo "OK" || echo "FAIL"

# Check latest upstream commit
echo "Latest upstream commit:"
git ls-remote https://github.com/acidanthera/OpenCorePkg.git refs/heads/master | cut -f1

# Check open PRs
echo "Open sync PRs:"
gh pr list --label "sync" --state open 2>/dev/null | wc -l

# Check failed workflows
echo "Failed workflows (last 24h):"
gh run list --status failure --limit 10 2>/dev/null | wc -l

# Check patch stack status
echo "Patches:"
for patch in Patches/*.patch; do
  echo -n "  $(basename $patch): "
  git am --check "$patch" 2>/dev/null && echo "OK" || echo "NEEDS REBASE"
done

echo "=== Health Check Complete ==="
```

---

## 16. Incident Response

### 16.1 Incident Classification

| Severidade | Descrição | Tempo de Resposta | Ação |
|---|---|---|---|
| P0 | Release com bug crítico, boot failure | 1 hora | Rollback imediato + hotfix |
| P1 | Pipeline quebrado, sync falhando | 4 horas | Investigar + corrigir |
| P2 | Teste intermitente, warning novo | 24 horas | Investigar + corrigir |
| P3 | Melhoria de performance, doc update | 1 semana | Backlog |

### 16.2 Rollback Procedure

```bash
# Rollback para release anterior
#!/bin/bash
set -euo pipefail

TARGET_RELEASE=$1  # ex: v1.242.0.0

echo "Rolling back to $TARGET_RELEASE..."

# 1. Checkout release tag
git checkout "$TARGET_RELEASE"

# 2. Create rollback branch
git checkout -b "rollback/$TARGET_RELEASE"

# 3. Force main to this point (requires admin)
git push origin "rollback/$TARGET_RELEASE" --force

# 4. Create rollback release
gh release create "rollback-$TARGET_RELEASE" \
  --title "Rollback to $TARGET_RELEASE" \
  --notes "Emergency rollback to $TARGET_RELEASE"

echo "Rollback complete. Verify builds and notify users."
```

### 16.3 Incident Runbook

1. **Detectar** — Monitoramento detecta anomalia
2. **Classificar** — Severidade P0/P1/P2/P3
3. **Conter** — Rollback se P0, hotfix se P1
4. **Investigar** — Root cause analysis
5. **Corrigir** — Hotfix PR com fix
6. **Verificar** — Todos os gates passam
7. **Documentar** — Post-mortem para P0/P1
8. **Prevenir** — Adicionar gate/teste se necessário

---

## 17. Patch Stack

### 17.1 Política de Patches

| Regra | Descrição |
|---|---|
| Mínimo | Número mínimo de patches locais |
| Documentado | Cada patch tem justificativa |
| Versionado | Patch stack tem versão própria |
| Aplicável | Patches devem ser rebaseáveis sobre upstream |
| Verificável | CI verifica que patches continuam aplicáveis |
| Auditable | Cada aplicação de patch é commit separado |

### 17.2 Estrutura de Patches

```
Patches/
├── 0001-MdeModulePkg-SataControllerDxe-Add-support-for-drive.patch
├── 0002-MdeModulePkg-AtaAtapiPassThru-Add-support-for-drives.patch
├── 0003-MdeModulePkg-AtaAtapiPassThru-Reduce-timeout.patch
├── 0005-ShellPkg-Devices-shell-command-support-misaligned-de.patch
├── 0007-ShellPkg-Allow-DEBUG-shell-to-start-with-too-many-fi.patch
└── README.md
```

### 17.3 Rebase Automático

```bash
#!/bin/bash
# scripts/rebase-patches.sh
set -euo pipefail

echo "Rebasing patches onto upstream..."

# Fetch latest upstream
git fetch origin master

# Create rebase branch
git checkout -b rebase-patches origin/master

# Apply each patch
for patch in Patches/*.patch; do
  echo "Applying: $patch"
  if ! git am "$patch"; then
    echo "CONFLICT: $patch"
    git am --abort
    echo "Manual resolution required for: $patch"
    exit 1
  fi
done

echo "All patches applied successfully."
git log --oneline -n $(ls Patches/*.patch | wc -l)
```

---

## 18. Upstream Conflict Strategy

### 18.1 Tipos de Conflito

| Tipo | Descrição | Resolução |
|---|---|---|
| Textual | Mesmo arquivo, linhas diferentes | Merge tool manual |
| Estrutural | Arquivo movido/renomeado | Verificar se patch ainda se aplica |
| Semântico | Lógica mudou mas texto não conflita | Revisar manualmente |
| Build | Conflito em DSC/DEC/FDF | Revisar dependências |

### 18.2 Processo de Resolução

1. **Detectar** — `git merge-tree` ou GitHub merge conflict indicator
2. **Classificar** — Tipo de conflito e patch envolvido
3. **Resolver** — Manualmente com justificativa
4. **Verificar** — Build + testes passam
5. **Documentar** — Commit message descreve resolução
6. **Auditar** — PR review com diff da resolução

### 18.3 Regras

| Regra | Descrição |
|---|---|
| Nunca mascarar | Conflito não resolvido = merge bloqueado |
| Sem force push | Nenhum force push para "resolver" conflito |
| Justificativa | Toda resolução tem commit message explicativa |
| Auditável | Resolução é commit separado do sync |
| Revisável | Conflitos em arquivos críticos exigem review humano |

---

## 19. Governança

### 19.1 Roles

| Role | Responsabilidade | Quem |
|---|---|---|
| Maintainer | Decisões de merge, patches, releases | Gabriel Stoltemberg |
| Bot | Sync, review, auto-merge, CI | GitHub Actions + custom bot |
| Upstream | Código base | acidanthera/OpenCorePkg |

### 19.2 Decision Process

| Decisão | Processo |
|---|---|
| Merge upstream sync | Automático (todos gates passam) |
| Aplicar patch local | Manual ( Maintainer aprova) |
| Criar release | Automático (se classificado como release-worthy) |
| Resolver conflito | Manual ( Maintainer resolve) |
| Hotfix | Manual ( Maintainer cria PR) |
| Configuração CI | Manual ( Maintainer aprova) |

### 19.3 ADRs Necessários

| ADR | Título | Status |
|---|---|---|
| ADR-001 | Branch model e merge strategy | Pendente |
| ADR-002 | Sync frequency e detection method | Pendente |
| ADR-003 | Validation pipeline completo | Pendente |
| ADR-004 | Impact classification rules | Pendente |
| ADR-005 | Release semver para fork | Pendente |
| ADR-006 | SBOM e provenance format | Pendente |
| ADR-007 | Patch stack policy | Pendente |
| ADR-008 | Conflict resolution process | Pendente |
| ADR-009 | QEMU boot test strategy | Pendente |
| ADR-010 | Observability e alerting | Pendente |
| ADR-011 | Incident response process | Pendente |
| ADR-012 | Security threat model | Pendente |
| ADR-013 | Auto-merge policy | Pendente |
| ADR-014 | Rollback procedure | Pendente |
| ADR-015 | Autonomous operation rules | Pendente |

---

## 20. Operação Autônoma

### 20.1 Automação Completa

| Operação | Frequência | Automação | Intervenção Humana |
|---|---|---|---|
| Fetch upstream | 15 min | Cron job | Nenhuma |
| Detectar commits | 15 min | Cron job | Nenhuma |
| Criar sync branch | Ao detectar | Bot | Nenhuma |
| Criar PR | Ao detectar | Bot | Nenhuma |
| Rodar CI | Ao criar PR | GitHub Actions | Nenhuma |
| Review bot | Ao criar PR | Bot | Nenhuma |
| Auto-merge | Ao passar gates | Bot | Nenhuma |
| Classificar impacto | Ao merge | Bot | Nenhuma |
| Criar release | Se release-worthy | Bot | Nenhuma |
| Gerar SBOM | Ao criar release | GitHub Actions | Nenhuma |
| Gerar checksums | Ao criar release | GitHub Actions | Nenhuma |
| Gerar provenance | Ao criar release | GitHub Actions | Nenhuma |
| Health check | 15 min | Cron job | Nenhuma |
| Rebase patches | Ao sync | Script | Nenhuma (se sucesso) |

### 20.2 Exceções (Intervenção Manual Necessária)

| Situação | Ação |
|---|---|
| Conflito de merge | Maintainer resolve manualmente |
| Patch não reaplicável | Maintainer atualiza patch |
| Build quebra | Maintainer investiga |
| Release com bug | Maintainer decide rollback |
| Security incident | Maintainer segue runbook |
| Upstream muda estrutura | Maintainer adapta scripts |

### 20.3 Cron Jobs

```yaml
# .github/workflows/sync.yml
name: Upstream Sync

on:
  schedule:
    - cron: '*/15 * * * *'  # A cada 15 minutos
  workflow_dispatch:

jobs:
  sync:
    name: Sync with Upstream
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0

      - name: Fetch upstream
        run: git fetch origin master

      - name: Check for new commits
        id: check
        run: |
          LOCAL=$(git rev-parse HEAD)
          REMOTE=$(git rev-parse origin/master)
          if [ "$LOCAL" = "$REMOTE" ]; then
            echo "status=no_change" >> $GITHUB_OUTPUT
          else
            echo "status=changed" >> $GITHUB_OUTPUT
            echo "remote_sha=$REMOTE" >> $GITHUB_OUTPUT
            echo "remote_date=$(git log -1 --format=%ci origin/master)" >> $GITHUB_OUTPUT
          fi

      - name: Create sync branch
        if: steps.check.outputs.status == 'changed'
        run: |
          git checkout -b sync/upstream
          git merge origin/master --no-edit
          git push origin sync/upstream --force

      - name: Create PR
        if: steps.check.outputs.status == 'changed'
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh pr create \
            --title "sync: merge upstream ${{ steps.check.outputs.remote_sha }}" \
            --body "Upstream commit: ${{ steps.check.outputs.remote_sha }}\nDate: ${{ steps.check.outputs.remote_date }}" \
            --base main \
            --head sync/upstream

      - name: Clean old sync PRs
        run: |
          gh pr list --label "sync" --state open --json number,headRefName | \
          jq -r '.[] | select(.headRefName == "sync/upstream") | .number' | \
          while read pr; do
            gh pr close $pr --comment "Superseded by newer sync"
          done
```

---

## 21. Critérios de Aceite

### 21.1 Para Cada Sync PR

- [ ] PR criado automaticamente com diff completo
- [ ] PR inclui link para commit upstream
- [ ] Todos os builds passam (Linux, macOS, Windows)
- [ ] Análise estática passa (shellcheck, prospector)
- [ ] QEMU boot test passa
- [ ] Patches locais continuam aplicáveis
- [ ] SBOM pode ser gerado
- [ ] Nenhum conflito aberto
- [ ] Bot aprova PR automaticamente
- [ ] Merge realizado via squash

### 21.2 Para Cada Release

- [ ] Release criada automaticamente após merge classificado
- [ ] SBOM incluído (CycloneDX JSON)
- [ ] Checksums incluídos (SHA256 + SHA512)
- [ ] Provenance incluído (SLSA)
- [ ] Release notes geradas
- [ ] Artefatos verificáveis
- [ ] Rastreabilidade: release ↔ upstream SHA ↔ fork SHA
- [ ] Semver correto

### 21.3 Para o Projeto Completo

- [ ] Upstream configurado permanentemente
- [ ] Sync automático funcionando (15 min)
- [ ] CI pipeline completa funcionando
- [ ] Auto-merge seguro funcionando
- [ ] Releases automáticas funcionando
- [ ] Patch stack mantido e versionado
- [ ] Conflitos detectados e reportados
- [ ] Rollback testado e funcional
- [ ] Observabilidade implementada
- [ ] Documentação completa e atualizada
- [ ] Operação autônoma com mínima intervenção

---

## 22. Riscos

| ID | Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|---|
| RK-001 | Upstream muda estrutura drasticamente | Baixa | Alto | Adaptar scripts, revisar patches |
| RK-002 | Patch local conflita com upstream | Média | Médio | Rebase automático + detecção |
| RK-003 | QEMU boot test é frágil | Média | Médio | Testes robustos, tolerância a flakiness |
| RK-004 | GitHub Actions tem downtime | Baixa | Alto | Retry logic, monitoring |
| RK-005 | Token GitHub é comprometido | Baixa | Crítico | Escopo mínimo, rotação |
| RK-006 | Upstream introduces breaking change | Média | Alto | Impact classifier + manual review |
| RK-007 | SBOM generation fails | Baixa | Médio | Fallback manual, alerta |
| RK-008 | Auto-merge permite merge quebrado | Baixa | Crítico | Múltiplos gates, nenhum bypass |
| RK-009 | Fork diverge silenciosamente | Média | Alto | Monitoramento de divergência |
| RK-010 | Mantainer indisponível | Média | Médio | Autonomia completa para sync routine |

---

## 23. Roadmap

### Fase 1: Foundation (Semanas 1-2)

| Item | Status | Prioridade |
|---|---|---|
| Configurar remote upstream | Pendente | Crítica |
| Branch protection em main | Pendente | Crítica |
| Workflow de sync (15 min) | Pendente | Crítica |
| Workflow de build (já existe) | Completo | - |
| Workflow de analyze (já existe) | Completo | - |
| Adicionar QEMU boot test | Pendente | Alta |
| Adicionar patch stack verify | Pendente | Alta |

### Fase 2: Automation (Semanas 3-4)

| Item | Status | Prioridade |
|---|---|---|
| Auto-merge com branch protection | Pendente | Alta |
| Bot de review automático | Pendente | Alta |
| Impact classifier | Pendente | Alta |
| PR template padronizado | Pendente | Média |

### Fase 3: Release (Semanas 5-6)

| Item | Status | Prioridade |
|---|---|---|
| Release pipeline (SBOM, checksums, provenance) | Pendente | Alta |
| Semver para fork | Pendente | Alta |
| Release notes automáticas | Pendente | Média |
| Rollback procedure | Pendente | Média |

### Fase 4: Observability (Semanas 7-8)

| Item | Status | Prioridade |
|---|---|---|
| Health check script | Pendente | Alta |
| Monitoring de métricas | Pendente | Média |
| Incident response runbook | Pendente | Média |
| Documentation completa | Pendente | Média |

### Fase 5: Hardening (Semanas 9-12)

| Item | Status | Prioridade |
|---|---|---|
| Security threat model completo | Pendente | Alta |
| ADRs documentados | Pendente | Média |
| Testes de rollback | Pendente | Média |
| Audit completo de autonomia | Pendente | Média |

---

## 24. ADRs Necessários

| ADR | Título | Decisão | Status |
|---|---|---|---|
| ADR-001 | Branch model | Squash merge, branch protection, sync branch temporária | Pendente |
| ADR-002 | Sync frequency | 15 minutos via cron | Pendente |
| ADR-003 | Validation pipeline | Build multi-plataforma + static + QEMU + patches | Pendente |
| ADR-004 | Impact classification | none/patch/minor/major/critical/infrastructure | Pendente |
| ADR-005 | Release semver | `v<upstream>.<fork_patch>` | Pendente |
| ADR-006 | SBOM format | CycloneDX JSON + SLSA provenance | Pendente |
| ADR-007 | Patch policy | Mínimo, documentado, versionado, verificável | Pendente |
| ADR-008 | Conflict resolution | Nunca mascarar, justificativa manual, auditável | Pendente |
| ADR-009 | QEMU boot test | OVMF boot em runner Linux | Pendente |
| ADR-010 | Observability | Prometheus/Grafana + health check script | Pendente |
| ADR-011 | Incident response | P0-P3 classification, runbook, rollback | Pendente |
| ADR-012 | Security model | Secret scanning, branch protection, SBOM, provenance | Pendente |
| ADR-013 | Auto-merge | Todos gates passam → auto-approve + merge | Pendente |
| ADR-014 | Rollback | Tag release anterior, force push main (admin only) | Pendente |
| ADR-015 | Autonomous operation | Sync 100% automático, manual apenas para exceções | Pendente |

---

## 25. Backlog Inicial

### 25.1 P0 — Crítico (Semana 1)

| ID | Item | Dependências |
|---|---|---|
| BK-001 | Configurar remote `origin` para upstream | Nenhuma |
| BK-002 | Configurar branch protection em `main` | BK-001 |
| BK-003 | Criar workflow `sync.yml` (15 min cron) | BK-001 |
| BK-004 | Criar workflow `test.yml` (QEMU boot) | Nenhuma |
| BK-005 | Criar workflow `patches.yml` (patch verify) | Nenhuma |

### 25.2 P1 — Alta (Semanas 2-3)

| ID | Item | Dependências |
|---|---|---|
| BK-006 | Configurar auto-merge com branch protection | BK-002, BK-003 |
| BK-007 | Criar bot de review automático | BK-003 |
| BK-008 | Implementar impact classifier | BK-003 |
| BK-009 | Criar PR template padronizado | Nenhuma |
| BK-010 | Documentar patches existentes | Nenhuma |

### 25.3 P2 — Média (Semanas 4-6)

| ID | Item | Dependências |
|---|---|---|
| BK-011 | Criar release pipeline (SBOM, checksums, provenance) | BK-006 |
| BK-012 | Implementar semver para fork | BK-011 |
| BK-013 | Criar release notes automáticas | BK-011 |
| BK-014 | Implementar rollback procedure | BK-011 |
| BK-015 | Criar health check script | BK-003 |

### 25.4 P3 — Baixa (Semanas 7-12)

| ID | Item | Dependências |
|---|---|---|
| BK-016 | Implementar monitoring (Prometheus/Grafana) | BK-015 |
| BK-017 | Criar incident response runbook | BK-014 |
| BK-018 | Documentar ADRs | Nenhuma |
| BK-019 | Audit completo de autonomia | Todos anteriores |
| BK-020 | Testes de rollback | BK-014 |

---

## 26. Métricas de Sucesso

| Métrica | Meta | Como Medir |
|---|---|---|
| Sync latency | < 15 min | Tempo entre commit upstream e PR |
| Pipeline duration | < 30 min | Duração do workflow |
| Pipeline success rate | > 98% | Workflows bem-sucedidos / total |
| Time to merge | < 1 hora | Tempo entre PR creation e merge |
| Patches rebased | 100% | Todos patches aplicam após sync |
| QEMU boot pass rate | 100% | Boot tests passam |
| Releases created | Automático | Releases criadas sem intervenção |
| Failed merges | 0 | Nenhum merge com gates vermelhos |
| Rollback time | < 5 min | Tempo para restaurar release anterior |
| Manual intervention | < 1/mês | Intervenções manuais necessárias |

---

## 27. Glossário

| Termo | Definição |
|---|---|
| Upstream | `acidanthera/OpenCorePkg` — repositório original |
| Fork | Este repositório — cópia gerenciada |
| Sync | Processo de incorporar commits upstream |
| Patch | Mudança local aplicada sobre upstream |
| Gate | Requisito que deve ser satisfeito antes de merge |
| SBOM | Software Bill of Materials — lista de componentes |
| Provenance | Declaração SLSA de origem dos artefatos |
| Impact | Classificação do efeito de um merge |
| Rollback | Reverter para release anterior |
| Auto-merge | Merge automático após gates passarem |

---

## 28. Referências

| Referência | URL |
|---|---|
| OpenCorePkg upstream | https://github.com/acidanthera/OpenCorePkg |
| OpenCore documentation | https://dortania.github.io/OpenCore-Install-Guide/ |
| SLSA provenance | https://slsa.dev/ |
| CycloneDX SBOM | https://cyclonedx.org/ |
| Semver | https://semver.org/ |
| GitHub Branch Protection | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-a-branch-protection-rule |

---

*Documento gerado em 2026-08-19. Sujeito a revisão e atualização conforme o projeto evolui.*
