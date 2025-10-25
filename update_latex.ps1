$ErrorActionPreference = 'Stop'
$path = 'c:\MAIN-PROJECT\health-data-exchange\main_updated.tex'
$bak = $path + '.bak.' + (Get-Date -Format 'yyyyMMddHHmmss')
Copy-Item $path $bak

# Read file
$txt = Get-Content -Raw -Path $path -Encoding UTF8

# 1) Move hyperref after tikz
$txt = $txt -replace '(?m)^\\usepackage\{hyperref\}\s*\r?\n',''
$txt = $txt -replace '(?m)(^\\usepackage\{tikz\}\s*\r?\n)','$1\\usepackage{hyperref}`r`n'

# 2) Replace abstract placeholder link with concrete URL
$repo = 'https://github.com/loki4968/PRIVACY-PRESERVING-HEALTH-DATA-EXCHANGE-USING-SECURE-MULTI-PARTY-COMPUTATION'
$replacementRepo = "\\url{" + [regex]::Escape($repo) + "}"
$txt = $txt -replace '\\[GitHub link or repository\\]',$replacementRepo

# 3) Insert Participation & Invitation Flow subsection before Evaluation and Results
$participation = @'
\\subsection{Participation and Invitation Flow}
The Coordinator issues targeted invitations so that organizations only view requests addressed to them. Invitees may accept or decline; transitions are audited with timestamps and actor IDs. This minimizes unnecessary visibility and aligns with least-privilege access control. Upon acceptance, participants upload encrypted shares or ciphertexts, and only final results are disclosed to authorized parties.
'@
$txt = [regex]::Replace($txt,'(?m)^\\section\{Evaluation and Results\}',$participation + "`r`n\\section{Evaluation and Results}")

# 4) Insert Catalog table before Evaluation and Results
$catalog = @'
% Catalog of supported analytics
\begin{table}[t]
\centering
\caption{Catalog of Supported Secure Analytics}
\label{tab:catalog}
\resizebox{\linewidth}{!}{
\begin{tabular}{lllc}
\toprule
\textbf{Category} & \textbf{Computation} & \textbf{Security} & \textbf{Typical Use Case} \\
\midrule
Statistical & Sum, Mean, Variance & Hybrid & Descriptive metrics \\
Statistical & Correlation & Hybrid & Feature association \\
Statistical & Linear Regression & SMPC & Risk modeling \\
Survival & Kaplan--Meier & SMPC & Outcome analysis \\
ML & Federated Logistic & SMPC & Classification \\
ML & Federated Random Forest & SMPC & Ensemble modeling \\
ML & Anomaly Detection & SMPC & Outlier screening \\
Healthcare & Cohort Analysis & SMPC & Trial cohort selection \\
Healthcare & Drug Safety & SMPC & ADR detection \\
Epidemiology & Surveillance & SMPC & Population trends \\
Genomics & Secure GWAS & Hybrid & SNP association \\
Genomics & Pharmacogenomics & Hybrid & Drug--gene effects \\
\bottomrule
\end{tabular}}
\end{table}
'@
$txt = [regex]::Replace($txt,'(?m)^\\section\{Evaluation and Results\}',$catalog + "`r`n\\section{Evaluation and Results}")

# 5) Insert Implementation Readiness table before System Architecture
$impl = @'
% Implementation readiness comparison
\begin{table}[t]
\centering
\caption{Implementation Readiness Across Related Work}
\label{tab:impl_readiness}
\resizebox{\linewidth}{!}{
\begin{tabular}{lccc}
\toprule
\textbf{Work} & \textbf{Prototype} & \textbf{Real-time/Live} & \textbf{Open Code} \\
\midrule
MedRec \cite{azaria2016medrec} & \checkmark & -- & -- \\
BBDS \cite{xia2017bbds} & \checkmark & -- & -- \\
MedShare \cite{xia2017medshare} & \checkmark & -- & -- \\
MP-SPDZ \cite{keller2020} & \checkmark & -- & \checkmark \\
PriCollab \cite{sunitha2024} & \checkmark & -- & -- \\
PriCollabAnalysis \cite{tawfik2025} & \checkmark & -- & -- \\
\textbf{Our Platform} & \checkmark & \checkmark & \checkmark \\
\bottomrule
\end{tabular}}
\end{table}
'@
$txt = [regex]::Replace($txt,'(?m)^\\section\{System Architecture\}',$impl + "`r`n\\section{System Architecture}")

# 6) Add Results dashboard figure and Reproducibility paragraph before Correctness Evaluation
$figure = @'
% Results dashboard illustration (shown if image exists)
\begin{figure}[t]
  \centering
  \IfFileExists{results_dashboard.png}{\includegraphics[width=\linewidth]{results_dashboard.png}}{\fbox{Results dashboard figure placeholder}}
  \caption{Results dashboard with statistical cards and visual analysis (bar, pie, line, and doughnut charts).}
  \label{fig:results-dashboard}
\end{figure}

\paragraph{Reproducibility} Experiments were run with Python 3.11 (FastAPI backend) and React/Next.js frontend. Fixed-point scaling was applied prior to sharing/encryption; SMPC thresholding and seeds were held constant across trials. The repository and instructions are available at \url{https://github.com/loki4968/PRIVACY-PRESERVING-HEALTH-DATA-EXCHANGE-USING-SECURE-MULTI-PARTY-COMPUTATION}.
'@
$txt = [regex]::Replace($txt,'(?m)^\\subsection\{Correctness Evaluation\}',$figure + "`r`n\\subsection{Correctness Evaluation}")

# 7) Append clarifications after the Shamir sentence in Formal Security Guarantees
$anchor = 'Our implementation leverages Shamir''s Secret Sharing with threshold $t = n-1$ to prevent reconstruction by fewer than $t+1$ parties.'
$add = ' In practice, additive aggregations prefer homomorphic addition to reduce interaction, while complex analytics (e.g., regression, survival) run under SMPC. Coefficient ranges and fixed-point scaling are bounded to avoid overflow and preserve numerical stability without degrading privacy guarantees.'
$txt = $txt -replace [regex]::Escape($anchor), ($anchor + $add)

# Save
[IO.File]::WriteAllText($path, $txt, [Text.UTF8Encoding]::new($false))
Write-Output ("UPDATED: {0} | Backup: {1}" -f $path, $bak)
