/**
 * ARGUS Frontend — React Interface
 * Interactive argument analysis and visualization
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Sword, 
  Shield, 
  GitBranch, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Target,
  TrendingUp,
  Brain
} from 'lucide-react';

// API Configuration
const API_BASE = 'http://localhost:8000';

// Types (matching backend)
interface AtomicClaim {
  id: string;
  text: string;
  claim_type: string;
  assumptions: string[];
  evidence_required?: string;
  confidence?: number;
  supports: string[];
  contradicts: string[];
}

interface CounterArgument {
  target_claim_id: string;
  attack_vector: string;
  counterpoint: string;
  supporting_evidence?: string;
  strength: number;
}

interface DefenseArgument {
  original_claim_id: string;
  strengthened_claim: string;
  additional_support: string[];
  removed_weaknesses: string[];
}

interface LogicalFallacy {
  fallacy_type: string;
  location: string;
  explanation: string;
  severity: 'minor' | 'moderate' | 'severe';
}

interface ArgumentGraph {
  original_input: string;
  claims: AtomicClaim[];
  fallacies: LogicalFallacy[];
  attacks: CounterArgument[];
  defenses: DefenseArgument[];
  robustness_score?: number;
  survived_claims: string[];
  collapsed_claims: string[];
  value_dependent_claims: string[];
}

const ArgumentAnalyzer: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [stance, setStance] = useState<'attack' | 'defense' | 'dialectic'>('dialectic');
  const [persona, setPersona] = useState('academic');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ArgumentGraph | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analyzeArgument = async () => {
    if (!inputText.trim()) {
      setError('Please enter an argument to analyze');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          input_text: inputText,
          stance,
          persona,
          detect_fallacies: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data.graph);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-5xl font-bold text-white tracking-tight">
            ARGUS
          </h1>
          <p className="text-xl text-slate-300">
            The Universal Argument Engine
          </p>
          <p className="text-sm text-slate-400 italic">
            "If it can be believed, ARGUS can argue it."
          </p>
        </div>

        {/* Input Section */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Brain className="w-5 h-5" />
              Enter Argument
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              placeholder="Enter any argument, belief, or claim... 
Examples:
• AI will replace doctors
• Free will doesn't exist
• Nigeria should ban crypto
• [Paste a tweet or paragraph]"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="min-h-[150px] bg-slate-900 border-slate-600 text-white placeholder:text-slate-500"
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-slate-300 mb-2 block">
                  Analysis Mode
                </label>
                <Select value={stance} onValueChange={(v: any) => setStance(v)}>
                  <SelectTrigger className="bg-slate-900 border-slate-600 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="attack">
                      <span className="flex items-center gap-2">
                        <Sword className="w-4 h-4" />
                        Attack (Devil's Advocate)
                      </span>
                    </SelectItem>
                    <SelectItem value="defense">
                      <span className="flex items-center gap-2">
                        <Shield className="w-4 h-4" />
                        Defense (Steelman)
                      </span>
                    </SelectItem>
                    <SelectItem value="dialectic">
                      <span className="flex items-center gap-2">
                        <GitBranch className="w-4 h-4" />
                        Dialectic (Full Debate)
                      </span>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm text-slate-300 mb-2 block">
                  Argument Style
                </label>
                <Select value={persona} onValueChange={setPersona}>
                  <SelectTrigger className="bg-slate-900 border-slate-600 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="academic">Academic</SelectItem>
                    <SelectItem value="engineer">Engineer</SelectItem>
                    <SelectItem value="politician">Politician</SelectItem>
                    <SelectItem value="economist">Economist</SelectItem>
                    <SelectItem value="twitter">Twitter</SelectItem>
                    <SelectItem value="reddit_atheist">Reddit Atheist</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Button
              onClick={analyzeArgument}
              disabled={loading || !inputText.trim()}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              {loading ? 'Analyzing...' : 'Analyze Argument'}
            </Button>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Results Section */}
        {result && (
          <div className="space-y-6">
            {/* Robustness Score */}
            <Card className="bg-gradient-to-r from-blue-900 to-purple-900 border-blue-700">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-2xl font-bold text-white mb-1">
                      Robustness Score
                    </h3>
                    <p className="text-blue-200">
                      How well does this argument withstand scrutiny?
                    </p>
                  </div>
                  <div className="text-6xl font-bold text-white">
                    {result.robustness_score?.toFixed(0) || 0}
                    <span className="text-2xl text-blue-300">/100</span>
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold text-green-400">
                      {result.survived_claims.length}
                    </div>
                    <div className="text-sm text-slate-300">Survived</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-red-400">
                      {result.collapsed_claims.length}
                    </div>
                    <div className="text-sm text-slate-300">Collapsed</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-yellow-400">
                      {result.value_dependent_claims.length}
                    </div>
                    <div className="text-sm text-slate-300">Value-Based</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Tabs for different views */}
            <Tabs defaultValue="claims" className="w-full">
              <TabsList className="grid w-full grid-cols-4 bg-slate-800">
                <TabsTrigger value="claims">Claims</TabsTrigger>
                <TabsTrigger value="attacks">Attacks</TabsTrigger>
                <TabsTrigger value="defenses">Defenses</TabsTrigger>
                <TabsTrigger value="fallacies">Fallacies</TabsTrigger>
              </TabsList>

              {/* Claims Tab */}
              <TabsContent value="claims" className="space-y-3">
                {result.claims.map((claim) => (
                  <ClaimCard
                    key={claim.id}
                    claim={claim}
                    survived={result.survived_claims.includes(claim.id)}
                    collapsed={result.collapsed_claims.includes(claim.id)}
                    valueDependent={result.value_dependent_claims.includes(claim.id)}
                  />
                ))}
              </TabsContent>

              {/* Attacks Tab */}
              <TabsContent value="attacks" className="space-y-3">
                {result.attacks.map((attack, idx) => (
                  <AttackCard key={idx} attack={attack} />
                ))}
              </TabsContent>

              {/* Defenses Tab */}
              <TabsContent value="defenses" className="space-y-3">
                {result.defenses.map((defense, idx) => (
                  <DefenseCard key={idx} defense={defense} />
                ))}
              </TabsContent>

              {/* Fallacies Tab */}
              <TabsContent value="fallacies" className="space-y-3">
                {result.fallacies.length === 0 ? (
                  <Alert className="bg-green-900 border-green-700">
                    <CheckCircle className="w-4 h-4" />
                    <AlertDescription className="text-green-100">
                      No logical fallacies detected!
                    </AlertDescription>
                  </Alert>
                ) : (
                  result.fallacies.map((fallacy, idx) => (
                    <FallacyCard key={idx} fallacy={fallacy} />
                  ))
                )}
              </TabsContent>
            </Tabs>
          </div>
        )}
      </div>
    </div>
  );
};

// Component: Claim Card
const ClaimCard: React.FC<{
  claim: AtomicClaim;
  survived: boolean;
  collapsed: boolean;
  valueDependent: boolean;
}> = ({ claim, survived, collapsed, valueDependent }) => {
  const statusIcon = survived ? (
    <CheckCircle className="w-5 h-5 text-green-400" />
  ) : collapsed ? (
    <XCircle className="w-5 h-5 text-red-400" />
  ) : (
    <Target className="w-5 h-5 text-yellow-400" />
  );

  const statusColor = survived
    ? 'border-green-700 bg-green-900/20'
    : collapsed
    ? 'border-red-700 bg-red-900/20'
    : 'border-yellow-700 bg-yellow-900/20';

  return (
    <Card className={`${statusColor} border`}>
      <CardContent className="pt-4">
        <div className="flex items-start gap-3">
          {statusIcon}
          <div className="flex-1 space-y-2">
            <p className="text-white font-medium">{claim.text}</p>
            
            <div className="flex gap-2 flex-wrap">
              <Badge variant="outline" className="text-xs">
                {claim.claim_type}
              </Badge>
              {valueDependent && (
                <Badge variant="outline" className="text-xs bg-yellow-900/30">
                  Value-Based
                </Badge>
              )}
            </div>

            {claim.assumptions.length > 0 && (
              <div className="mt-2">
                <p className="text-sm text-slate-400 mb-1">Assumptions:</p>
                <ul className="text-sm text-slate-300 space-y-1">
                  {claim.assumptions.map((assumption, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-slate-500">•</span>
                      <span>{assumption}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Component: Attack Card
const AttackCard: React.FC<{ attack: CounterArgument }> = ({ attack }) => {
  const strengthPercent = Math.round(attack.strength * 100);
  const strengthColor =
    strengthPercent >= 70 ? 'text-red-400' : strengthPercent >= 40 ? 'text-yellow-400' : 'text-blue-400';

  return (
    <Card className="bg-red-900/10 border-red-800">
      <CardContent className="pt-4">
        <div className="flex items-start gap-3">
          <Sword className="w-5 h-5 text-red-400 mt-1" />
          <div className="flex-1">
            <div className="flex items-center justify-between mb-2">
              <Badge variant="outline" className="text-xs">
                {attack.attack_vector.replace(/_/g, ' ')}
              </Badge>
              <span className={`text-sm font-bold ${strengthColor}`}>
                {strengthPercent}% strength
              </span>
            </div>
            <p className="text-white">{attack.counterpoint}</p>
            {attack.supporting_evidence && (
              <p className="text-sm text-slate-400 mt-2">
                Evidence: {attack.supporting_evidence}
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Component: Defense Card
const DefenseCard: React.FC<{ defense: DefenseArgument }> = ({ defense }) => (
  <Card className="bg-green-900/10 border-green-800">
    <CardContent className="pt-4">
      <div className="flex items-start gap-3">
        <Shield className="w-5 h-5 text-green-400 mt-1" />
        <div className="flex-1 space-y-3">
          <div>
            <p className="text-sm text-slate-400 mb-1">Strengthened Claim:</p>
            <p className="text-white font-medium">{defense.strengthened_claim}</p>
          </div>

          {defense.additional_support.length > 0 && (
            <div>
              <p className="text-sm text-slate-400 mb-1">Additional Support:</p>
              <ul className="text-sm text-slate-300 space-y-1">
                {defense.additional_support.map((support, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-green-500">✓</span>
                    <span>{support}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </CardContent>
  </Card>
);

// Component: Fallacy Card
const FallacyCard: React.FC<{ fallacy: LogicalFallacy }> = ({ fallacy }) => {
  const severityColor = {
    minor: 'border-yellow-700 bg-yellow-900/20',
    moderate: 'border-orange-700 bg-orange-900/20',
    severe: 'border-red-700 bg-red-900/20',
  }[fallacy.severity];

  return (
    <Card className={severityColor}>
      <CardContent className="pt-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-orange-400 mt-1" />
          <div className="flex-1">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-bold text-white">
                {fallacy.fallacy_type.replace(/_/g, ' ').toUpperCase()}
              </h4>
              <Badge variant="outline" className="text-xs">
                {fallacy.severity}
              </Badge>
            </div>
            <p className="text-slate-300 text-sm mb-2">{fallacy.explanation}</p>
            <p className="text-xs text-slate-500">Location: {fallacy.location}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ArgumentAnalyzer;
